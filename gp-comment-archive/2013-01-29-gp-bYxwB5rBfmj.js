[["Diana", "https://plus.google.com/118433478854468966061", "gp-1359577448964", "<p>Followed link from \n@<a href=\"https://plus.google.com/110320404823735193127\">Tim</a>\n\u00a0. \u00a0This is awesome.\n<br>\n<br>\nI'd like to see $/sq ft, too. \u00a0I'm skeptical about bedrooms, because I know lots of apartments are advertised by room, so as to appeal to people who want roommates and those who don't.\n<br>\n<br>\nI'd also love to see where the T stops are on the map, because I wonder how many of those little pockets of orange/red are clustered around them.\n<br>\n<br>\ni didn't even know google supported heatmaps. \u00a0so cool.</p>", 1359577448], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1359578214691", "<p>@<a href=\"https://plus.google.com/118433478854468966061\">Diana</a>\n\u00a0\"I'd like to see $/sq ft, too\"\n<br>\n<br>\nUnfortunately people don't usually post square footage on craigslist, and even when they do I don't think padmapper collects that data. \u00a0If we had it though, I agree it would be ideal.\n<br>\n<br>\n\"I know lots of apartments are advertised by room, so as to appeal to people who want roommates and those who don't.\"\n<br>\n<br>\nWhat do you mean? \u00a0Nearly all apartments I see are advertised as 1br, 2br, 3br, studio, etc. \u00a0That's the data padmapper is collecting, and both maps are based off that. \u00a0The $/bedroom map is straight up cost/bedrooms while the $/room map is cost/(bedrooms + 1) because a 2br is usually a three room apartment etc.\n<br>\n<br>\n\"I'd also love to see where the T stops are on the map, because I wonder how many of those little pockets of orange/red are clustered around them.\"\n<br>\n<br>\nSomeone on reddit wondered the same thing and made a map:\u00a0\n<a href=\"http://i.imgur.com/Tub0BMD.jpg\">http://i.imgur.com/Tub0BMD.jpg</a>\n \u00a0comments:\u00a0\n<a href=\"http://www.reddit.com/r/boston/comments/17kd4b/2013_boston_rental_heat_map_with_added_tstops/\">http://www.reddit.com/r/boston/comments/17kd4b/2013_boston_rental_heat_map_with_added_tstops/</a>\n<br>\n<br>\n\"I didn't even know google supported heatmaps\"\n<br>\n<br>\nIt doesn't. \u00a0I made the heatmap myself and the mashup is google maps plus an appropriate image.</p>", 1359578214], ["Galen", "https://plus.google.com/113853090979911392217", "gp-1359654886178", "<p>I like this visualization, but I think there's a problem in Jamaica Plain and Roxbury. The residential streets between Egleston Square and Franklin Park come up among the most expensive neighborhoods, colored in red. One small section of Uphams Corner shows the same. I've never looked at rental listings in either place, but I live near Egleston. I doubt very much that rents here or in Uphams are equal to those in the South End.</p>", 1359654886], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1359656530358", "<p>@<a href=\"https://plus.google.com/113853090979911392217\">Galen</a>\n\u00a0That looks like one listing that's way too high. \u00a0Looking into it, it's a commercial listing (so \"0br\") that shouldn't have been in the data. \u00a0I just manually checked the rest of the really high listings, removing three other bogus ones, and am regenerating the maps. \u00a0Thanks!\n<br>\n<br>\n(Another thing I found is that the way I'm getting data from padmapper limits apartments to $6k. \u00a0So ones more expensive than that are rounded down to $6k. \u00a0In checking for bogus ones I also corrected some of these, so I expect a bit more red, in the right places, on the new maps when they finish.)</p>", 1359656530], ["Nathan", "https://plus.google.com/115047443549315712634", "gp-1359661319862", "<p>Hi, Jeff. \u00a0Thanks for the github code. \u00a0After generating apts.png, how did you overlay it on the Google Map online?</p>", 1359661319], ["Galen", "https://plus.google.com/113853090979911392217", "gp-1359664138233", "<p>@<a href=\"https://plus.google.com/103013777355236494008\">Jeff&nbsp;Kaufman</a>\n\u00a0Nice. Looking at it first off, I thought it might be a geocoding problem. I wouldn't be surprised to find a hot spot of relatively high rents of about the same size, a little north of there in Fort Hill, which has a great view of Downtown from the summit. (The park there is a great spot to watch the fireworks on July 4.)\u00a0</p>", 1359664138], ["Marcus", "https://plus.google.com/111675838261170541573", "gp-1359674320241", "<p>Nice job. I will note that my experience from watching a friend search for rooms on padmapper recently is that Nigerian* scammers have taken to posting false ads for apartments, usually at better rates than the area average, so that might pull your data down a bit compared to reality.\n<br>\n<br>\n*When contacted, it would turn out the landlord was out of town, often supposedly in Nigeria, and the first steps of the conversation looked suspiciously like they were leading up to \"mail me money in return for my mailing you a key\" or \"provide me enough personal details in the info-exchange process to do an identity theft\". (one interesting answer to 'why Nigeria?' is at \n<a href=\"http://research.microsoft.com/pubs/167719/WhyFromNigeria.pdf\">http://research.microsoft.com/pubs/167719/WhyFromNigeria.pdf</a>\n)</p>", 1359674320], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1359733355176", "<p>@<a href=\"https://plus.google.com/113853090979911392217\">Galen</a>\n\u00a0I've uploaded the revised maps.</p>", 1359733355], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1359733433906", "<p>@<a href=\"https://plus.google.com/115047443549315712634\">Nathan</a>\n\u00a0\"how did you overlay it on the Google Map online?\"\n<br>\n<br>\nHave a look at the source, with pagespeed disabled: \n<a href=\"http://www.jefftk.com/apartment_prices/index?ModPagespeed=off\">http://www.jefftk.com/apartment_prices/index?ModPagespeed=off</a></p>", 1359733433], ["Diana", "https://plus.google.com/118433478854468966061", "gp-1359738049127", "<p>\"I know lots of apartments are advertised by room, so as to appeal to people who want roommates and those who don't.\"\n<br>\n<br>\nWhat I mean is that a lot of apartments have \"rooms\" that might be considered bedrooms, or might not, depending on who is living there. \u00a0How they are listed depends on whether the landlord wants to appeal to people who want cheaper housing (3BR = 3 roommates = shared costs = probably college kids), or higher end housing (1 BR + office + storage closet = single or couple = higher cost per = older professional type).\n<br>\n<br>\nWhen I a young professional, I lived in 3rd floor walk-up in Somerville that in theory had 3BR, but really, one of those BRs was a glorified closet, and the other was barely better -- i used it as an office. \u00a0In my mind it was a 1+BR, but before me it had been occupied by three college students. \u00a0That same apartment, had it been in a higher rent district rather than right across the street from Tufts, would probably have been advertised as a 1 or 2BR...even if the rent had been the same. \u00a0 \u00a0Thus the \"per bedroom\" cost on your map would have been artificially raised.\n<br>\n<br>\nNumber of rooms is less fungible than number of bedrooms. \u00a0Square footage is less fungible still.</p>", 1359738049], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1359739911779", "<p>@<a href=\"https://plus.google.com/118433478854468966061\">Diana</a>\n\u00a0\"Number of rooms is less fungible than number of bedrooms. \u00a0Square footage is less fungible still.\"\n<br>\n<br>\nMakes sense. \u00a0If padmapper collected those I'd plot them.</p>", 1359739911], ["Alex", "https://plus.google.com/100936518160252317727", "gp-1360510218333", "<p>Others may be interested in this DC heat map I just found:\u00a0\n<a href=\"http://welovedc.com/heatmap/\">http://welovedc.com/heatmap/</a></p>", 1360510218], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1360518191708", "<p>@<a href=\"https://plus.google.com/100936518160252317727\">Alex</a>\n\u00a0added it to the post. I also made ones for Atlanta and Baltimore.</p>", 1360518191], ["Alex", "https://plus.google.com/100936518160252317727", "gp-1360519320689", "<p>@<a href=\"https://plus.google.com/103013777355236494008\">Jeff&nbsp;Kaufman</a>\n\u00a0Awesome. Atlanta looks pretty spotty everywhere except right downtown, probably since it's so much less dense a city than Boston or Baltimore. I'm sure you've thought of this, but one could imagine building a much better interpolation of sparser cities if Padmapper offered historical data.</p>", 1360519320], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1360523714659", "<p>@<a href=\"https://plus.google.com/100936518160252317727\">Alex</a>\n\u00a0Historical data would help a lot.\n<br>\n<br>\nI could relax my coloring rules and make Atlanta less spotty, but only if price variation in less dense cities is longer wavelength.</p>", 1360523714]]