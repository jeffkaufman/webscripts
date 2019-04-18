[["Todd", "https://plus.google.com/112947709146257842066", "gp-1343422119073", "<p>Where are you getting this data? I'd be interested in replicating it for other cities.</p>", 1343422119], ["David&nbsp;Chudzicki", "https://plus.google.com/106120852580068301475", "gp-1343423458715", "<p>Thanks again, Jeff! I used your code to start making a map of my location (\n<a href=\"http://www.learnfromdata.com/location_map/\">http://www.learnfromdata.com/location_map/</a>\n).\u00a0\n<br>\n<br>\n(Should have used RGBA like you, though.)</p>", 1343423458], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1343424572810", "<p>@<a href=\"https://plus.google.com/112947709146257842066\">Todd</a>\n\u00a0See the previous post [1] for more details, but the data came from padmapper, which scrapes craigslist. \u00a0While they have nationwide data, you can't just download a dump. \u00a0Instead I pulled the data from an undocumented part of padmapper's api that has since changed. \u00a0So I don't have an easy way to update this data or get it for other cities. \u00a0Sorry!\n<br>\n<br>\n[1]\u00a0\n<a href=\"http://www.jefftk.com/news/2011-06-18.html\">http://www.jefftk.com/news/2011-06-18.html</a></p>", 1343424572], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1343424701246", "<p>@<a href=\"https://plus.google.com/106120852580068301475\">David&nbsp;Chudzicki</a>\n\u00a0Really neat! \u00a0Apparently you spend a lot of time on roads.\n<br>\n<br>\nWith the black-and-white I can't figure out how to tell the difference between places you've been once and places you spend a lot of time.\n<br>\n<br>\nIt would be nice if latitude offered a heatmap viewer.</p>", 1343424701], ["David&nbsp;Chudzicki", "https://plus.google.com/106120852580068301475", "gp-1343426144018", "<p>@<a href=\"https://plus.google.com/103013777355236494008\">Jeff&nbsp;Kaufman</a>\n\u00a0I stopped messing around with it while I was still trying to get the scaling right to show places I am more often. But no! That's just a couple road trips into the valley. I don't go that way often, and when I do it's usually by train.\n<br>\n<br>\nI'll let you know when I've fixed it. My end goal is really to make location predictions (for a point in the future), and use a heatmap to display the probability density of the predictions.\n<br>\n<br>\nI've been meaning to start logging your location for more data, but haven't yet.</p>", 1343426144], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1343528495143", "<p>@<a href=\"https://plus.google.com/106120852580068301475\">David&nbsp;Chudzicki</a>\n\u00a0\"I've been meaning to start logging your location for more data, but haven't yet.\"\n<br>\n<br>\nGoogle is saving it for me, so at some point I could just give you a data dump. \u00a0But they don't seem to offer a \"download all my location-timestamp pairs forever\" option. \u00a0Just download the last 30 days.\n<br>\n<br>\nMaking pretty maps would also be a great built-in feature for latitude.</p>", 1343528495], ["David&nbsp;Chudzicki", "https://plus.google.com/106120852580068301475", "gp-1343534006962", "<p>Yeah, I started using Geoloqi, partly b/c getting data out of Google was annoying. </p>", 1343534006], ["Jeremy", "https://plus.google.com/103590581158790876995", "gp-1343685051883", "<p>My own experience with craigslist, as I'm sure many of us have observed, is that good deals go quickly and bad deals stick around for a long time.\u00a0 If this effect in fact holds true generally there by averaging prices on listings taken during a given time period, then the overall prices may be biased high.\u00a0 One interesting source of data in some cities may be from rent control databases.\u00a0 For instance, the City of Berkeley allows you to look up the current rental status and rent ceiling by address (which includes the date the tenancy started), and the database seems to include the number of bedrooms as well.\u00a0 The rent ceilings aren't guaranteed to be equal to the rent being charged, but for recently started tenancies they pretty much are.\u00a0 Certainly this database may have some information missing or otherwise be inaccurate, but for many purposes it may be more reliable than Craigslist.</p>", 1343685051], ["David&nbsp;Chudzicki", "https://plus.google.com/106120852580068301475", "gp-1343685318895", "<p>...but due to rent ceilings, might not reflect what a new tenant will pay, right?\u00a0\n<br>\n<br>\n(I'm not sure about Berkeley, but the way rent ceilings mostly work in SF is to restrict how much you can raise rent on current tenants, but leave landlords free to charge what they want to new ones.)</p>", 1343685318], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1343685322791", "<p>@<a href=\"https://plus.google.com/103590581158790876995\">Jeremy</a>\n\u00a0\"by averaging prices on listings taken during a given time period, the overall prices may be biased high\"\n<br>\n<br>\nI hadn't thought of that, but it makes sense.\n<br>\n<br>\nAs for rent control databases, you're going to be limited by rent control being rare.</p>", 1343685322], ["Jeremy", "https://plus.google.com/103590581158790876995", "gp-1343686311631", "<p>@<a href=\"https://plus.google.com/106120852580068301475\">David&nbsp;Chudzicki</a>\n \"but due to rent ceilings\"\n<br>\nCertainly a rent ceiling for a tenancy started 10 years ago will be much lower than the current price for a new rental, but if you just look at rent ceilings for tenancies started in the past few months, I imagine it would reflect current prices pretty well.</p>", 1343686311], ["Jeremy", "https://plus.google.com/103590581158790876995", "gp-1343686488891", "<p>Note: In Berkeley, as I imagine is the case with most rent control schemes, the rent ceiling is equal to the negotiated rent at the time the tenancy started, plus some small rate of inflation per year.</p>", 1343686488], ["David&nbsp;Chudzicki", "https://plus.google.com/106120852580068301475", "gp-1343686559480", "<p>@<a href=\"https://plus.google.com/103590581158790876995\">Jeremy</a>\n\u00a0Ah, yeah.</p>", 1343686559]]