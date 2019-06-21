[["Jan-Willem", "https://plus.google.com/100580955183019057735", "gp-1377383927454", "<p>You've seen \n<a href=\"http://research.swtch.com/zip\">http://research.swtch.com/zip</a></p>", 1377383927], ["Jan-Willem", "https://plus.google.com/100580955183019057735", "gp-1377392626538", "<p>Whoops, that got truncated. \u00a0I had a colleague who had a \"zip bomb\" file on his site for a long time, but I think that bug got fixed. \u00a0The reason you're seeing less than the theoretical maximum I think is that gzip does some framing on the file which has a few bytes of overhead. \u00a0This allows the compressor to do stuff like decide not to encode chunks of the file if it contains a mix of already-compressed and compressible content. \u00a0It's why you can sometimes usefully gzip metadata-heavy image files even though gzipping an ordinary image file generally makes it bigger.</p>", 1377392626], ["Eric", "https://plus.google.com/113202109784097860410", "gp-1377452188279", "<p>Have you looked at SDCH? I haven't been able to find the details of how it works, so I have looked at xdelta, which it is loosely based on. \u00a0With a 1k dictionary of zeros a 1GB zero file compresses down to\u00a04243 for a ratio of\u00a0203862X. \u00a0The other data points I used suggest that it reaches a limit near 240,000X But I don't have the disk space to test fully.</p>", 1377452188]]