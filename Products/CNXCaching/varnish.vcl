backend backend {
  .host = "localhost";
  .port = "8880";
  .connect_timeout = 0.4s;
  .first_byte_timeout = 300s;
  .between_bytes_timeout = 60s;
}

acl purge {
    "localhost";
    "127.0.0.1";
}

sub vcl_recv {
    set req.grace = 120s;
    set req.backend = backend;

    if (req.request == "PURGE") {
        if (!client.ip ~ purge) {
                error 405 "Not allowed.";
        }
        set req.url = req.url "$";
        purge_url(req.url);
        log "purge url: " req.url;
        error 200 "Purged";
    }
    if (req.request == "PURGE_REGEXP") {
        if (!client.ip ~ purge) {
                error 405 "Not allowed.";
        }
        purge_url(req.url);
        log "purge regexp: " req.url;
        error 200 "Purged";
    }

    if (req.request != "GET" && req.request != "HEAD") {
        # We only deal with GET and HEAD by default
        return(pass);
    }
    call normalize_accept_encoding;
    call annotate_request;
    return(lookup);
}

sub vcl_fetch {
    if (!beresp.cacheable) {
        set beresp.http.X-Varnish-Action = "FETCH (pass - not cacheable)";
        return(pass);
    }
    #if (beresp.http.Set-Cookie) {
    #    set beresp.http.X-Varnish-Action = "FETCH (pass - response sets cookie)";
    #    return(pass);
    #}
    if (!beresp.http.Cache-Control ~ "s-maxage=[1-9]" && beresp.http.Cache-Control ~ "(private|no-cache|no-store)") {
        set beresp.http.X-Varnish-Action = "FETCH (pass - response sets private/no-cache/no-store token)";
        return(pass);
    }
    if (req.http.Authorization && !beresp.http.Cache-Control ~ "public") {
        set beresp.http.X-Varnish-Action = "FETCH (pass - authorized and no public cache control)";
        return(pass);
    }
    if (req.http.X-Anonymous && !beresp.http.Cache-Control) {
        set beresp.ttl = 600s;
        set beresp.http.X-Varnish-Action = "FETCH (override - backend not setting cache control)";
    }
    call rewrite_s_maxage;
    return(deliver);
}

sub vcl_deliver {
    if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT";
    } else {
        set resp.http.X-Cache = "MISS";
    }

    call rewrite_age;
}


##########################
#  Helper Subroutines
##########################

# Optimize the Accept-Encoding variant caching
sub normalize_accept_encoding {
    if (req.http.Accept-Encoding) {
        if (req.url ~ "\.(jpe?g|png|gif|swf|pdf|gz|tgz|bz2|tbz|zip)$" || req.url ~ "/image_[^/]*$") {
            remove req.http.Accept-Encoding;
        } elsif (req.http.Accept-Encoding ~ "gzip") {
            set req.http.Accept-Encoding = "gzip";
        } else {
            remove req.http.Accept-Encoding;
        }
    }
}

# Keep auth/anon variants apart if "Vary: X-Anonymous" is in the response
sub annotate_request {
    # X-Collection
    if (req.http.cookie ~ "(^|.*; )courseURL=") {
        set req.http.X-Collection = regsub(req.http.cookie, "^.*?courseURL=([^;]*);*.*$", "\1");
    }
    if (!(req.http.Authorization || req.http.cookie ~ "(^|.*; )__ac=" || req.http.cookie ~ "(^|.*; )cosign")) {
        set req.http.X-Anonymous = "True";
    }
    if (req.http.Accept ~ "application\/xhtml\+xml") {
        set req.http.X-Content-Type = "application/xhtml+xml";
    } else {
        set req.http.X-Content-Type = "text/html";
    }

}

# The varnish response should always declare itself to be fresh
sub rewrite_age {
    if (resp.http.Age) {
        set resp.http.X-Varnish-Age = resp.http.Age;
        set resp.http.Age = "0";
    }
}

# Rewrite s-maxage to exclude from intermediary proxies
# (to cache *everywhere*, just use 'max-age' token in the response to avoid this override)
sub rewrite_s_maxage {
    if (beresp.http.Cache-Control ~ "s-maxage") {
        set beresp.http.Cache-Control = regsub(beresp.http.Cache-Control, "s-maxage=[0-9]+", "s-maxage=0");
    }
}
