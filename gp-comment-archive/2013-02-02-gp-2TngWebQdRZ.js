[["Kit", "https://plus.google.com/109259097847092849006", "gp-1359841533241", "<p>Yes, it should.</p>", 1359841533], ["Chris", "https://plus.google.com/109145929828138109979", "gp-1359845139376", "<p>Or more simply, just invalidate its cache. No point in pre-reading a .htaccess in a rare URL</p>", 1359845139], ["James", "https://plus.google.com/106345404829653994850", "gp-1359851153752", "<p>Is it really rereading the file, or is it just reading the mtime? And how much does reading a cache-warm file's mtime cost, anyways? (My model says that it should be very cheap, unless the OS is being very stupid.)</p>", 1359851153], ["Lex", "https://plus.google.com/111102660583646544610", "gp-1359994157986", "<p>Sounds good to me.\n<br>\n<br>\nAlthough, I must say it has been a while since I ran into a true shared Unix box. Nowadays it's always\u00a0either a one-user machine, or a corporate machine where everyone has root. On such a machine, it seems just as well to manipulate the global configuration as to use .htacces files.</p>", 1359994157], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1360077851932", "<p>@<a href=\"https://plus.google.com/109145929828138109979\">Chris</a>\n\u00a0\n@<a href=\"https://plus.google.com/106345404829653994850\">James</a>\n\u00a0I looked into the code, and it turns out Apache doesn't cache htaccess files between requests:\u00a0\n<a href=\"http://www.jefftk.com/news/2013-02-05\">http://www.jefftk.com/news/2013-02-05</a></p>", 1360077851]]