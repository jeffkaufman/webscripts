[["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1432065473790", "<p>@<a href=\"https://plus.google.com/114552443805676710515\">Ilya</a>\n\u00a0\n@<a href=\"https://plus.google.com/110292420930947286319\">Josh</a>\n\u00a0</p>", 1432065473], ["Jan-Willem", "https://plus.google.com/100580955183019057735", "gp-1432073103005", "<p>So the browser is taking the pushed 304 as an empty pushed resource? \u00a0That'll be annoying to fix, I bet.</p>", 1432073103], ["Ilya", "https://plus.google.com/114552443805676710515", "gp-1432076358974", "<p>@<a href=\"https://plus.google.com/103013777355236494008\">Jeff&nbsp;Kaufman</a>\n\u00a0node-http2 should work, I was playing with it earlier today. Guessing, it's bailing due to some TLS misconfiguration -- HTTP/2 is much stricter about valid certs and all that stuff.\u00a0\n<br>\n<br>\nMore importantly though.. The 304 + Server Push does (almost) work:\u00a0\n<a href=\"https://gist.github.com/igrigorik/84e79bfb97ebc90ca553\">https://gist.github.com/igrigorik/84e79bfb97ebc90ca553</a>\n -- see the netlog trace. On first request (\"/\") the client requests script.js file by itself and gets a Last-Modified timestamp. Then, when the client hits \"/?next\" we push a 304 against script.js and the push stream is \"adopted\".\n<br>\n<br>\nThat said, see the gotcha note in the server.rb file: pushing a 304 against a non-existent record creates it in the Chrome cache.. with an empty body. FWIW, this doesn't seem right, it seems like Chrome should discard such entries -- if that's doable, then I think this technique would actually work quiet well.\n<br>\n<br>\n/cc \n@<a href=\"https://plus.google.com/116582795487334635924\">Chris</a>\n\u00a0\n@<a href=\"https://plus.google.com/100166083286297802191\">Patrick</a></p>", 1432076358], ["Mark", "https://plus.google.com/117348597427239540873", "gp-1433914677273", "<p>The other way to go about it is to push the 200, but for 1RT after the response headers have gone out, give the stream a lower weight. That covers this case as well when the cache is empty.</p>", 1433914677], ["Ilya", "https://plus.google.com/114552443805676710515", "gp-1433916753406", "<p>@<a href=\"https://plus.google.com/117348597427239540873\">Mark</a>\n\u00a0as in, 200 marks the previous response body as \"valid\" which allows the UA to read it from cache (hence the 1RT delay)? Because if so, then that seems kinda risky.. the 200 could be for an alternative response, it seems UA should block and wait.\u00a0</p>", 1433916753], ["Mark", "https://plus.google.com/117348597427239540873", "gp-1433916808899", "<p>@<a href=\"https://plus.google.com/114552443805676710515\">Ilya</a>\n\u00a0200 + response headers (which includes the etag)</p>", 1433916808], ["Ilya", "https://plus.google.com/114552443805676710515", "gp-1433916976466", "<p>@<a href=\"https://plus.google.com/117348597427239540873\">Mark</a>\n\u00a0ah, interesting. Hmm, how is that better than browser processing the pushed 304? The empty cache scenario there is: push 304, client drops it because there is no such cache entry and requests resource as usual.</p>", 1433916976], ["Mark", "https://plus.google.com/117348597427239540873", "gp-1433917121763", "<p>@<a href=\"https://plus.google.com/114552443805676710515\">Ilya</a>\n\u00a0having an extra RT's worth of response body (admittedly at diminished rate), having response headers immediately.</p>", 1433917121], ["Ilya", "https://plus.google.com/114552443805676710515", "gp-1433918382880", "<p>@<a href=\"https://plus.google.com/117348597427239540873\">Mark</a>\n\u00a0I see, but it also has the downside of incurring that RT's worth of response on revalidation's..</p>", 1433918382], ["Mark", "https://plus.google.com/117348597427239540873", "gp-1433918579963", "<p>@<a href=\"https://plus.google.com/114552443805676710515\">Ilya</a>\n\u00a0Yeah; it's a balance / judgement call. If we're talking about \nreally\n short freshness lifetimes, you're betting for/against the cache eviction algorithm + cache size / activity.</p>", 1433918579]]