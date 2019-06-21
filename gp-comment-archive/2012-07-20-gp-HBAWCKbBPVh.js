[["Todd", "https://plus.google.com/112947709146257842066", "gp-1342833356336", "<p>Couldn't you just use the +/@ tagging? That would reduce the number of successes, but it would also make the problem a lot more manageable, and I think people could train themselves to always use it (I already try to for clarity's sake, though I do forget sometimes).</p>", 1342833356], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342835302807", "<p>@<a href=\"https://plus.google.com/112947709146257842066\">Todd</a>\n\u00a0That might work, but there are also a lot of times when there are multiple things someone has said and you're only responding to one of them. \u00a0Certainly easier, though.</p>", 1342835302], ["James", "https://plus.google.com/106345404829653994850", "gp-1342842809723", "<p>This seems upside-down. If it's foreach(comment) foreach(earlier-comment last-first) instead of foreach(comment) foreach(later-comment earliest-first), then if there are multiple matches, the first match (in traversal order) will be the best parent. If you do it in a different order, then you run into problems when comments contain nested quotes.</p>", 1342842809], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342873742620", "<p>@<a href=\"https://plus.google.com/105024376133521186824\">Lucas</a>\n\u00a0What I'm planning to do is something like:\n<br>\n<br>\n1. identify all quotations\n<br>\n2. throw away records for comments that quote multiple comments\n<br>\n3. move each quoting comment to be a child of the comment it quotes\n<br>\n<br>\nThe second two steps are fast and straightforward, so I don't think they're so interesting unless they let us improve the first step.</p>", 1342873742], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342874548219", "<p>@<a href=\"https://plus.google.com/105024376133521186824\">Lucas</a>\n\u00a0I've added an O(n*m) implementation to the post.</p>", 1342874548], ["Alex", "https://plus.google.com/100936518160252317727", "gp-1342875181960", "<p>Sigh\n... If only the system included the comment we are replying to in some sort of standard way... maybe we could start with a standard string like \"on such-and-such a time, so-and-so wrote\", then include the comment with, say, angle brackets on each line to indicate a quote... and it would be a network for users, so we could call it Usenet! Oh wait.</p>", 1342875181], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342878259203", "<p>Threading added. \u00a0See \n<a href=\"http://www.jefftk.com/news/2012-03-24.html\">http://www.jefftk.com/news/2012-03-24.html</a>\n for an example of it working.</p>", 1342878259], ["Alex", "https://plus.google.com/100936518160252317727", "gp-1342879550468", "<p>@<a href=\"https://plus.google.com/103013777355236494008\">Jeff&nbsp;Kaufman</a>\n\u00a0it looks good!</p>", 1342879550], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342885508708", "<p>@<a href=\"https://plus.google.com/105024376133521186824\">Lucas</a>\n\u00a0\"if conversations ever go to more than one level of replies the layout gets a bit cramped\"\n<br>\n<br>\nWhat if I use css to make 'blockquote' shift the whole reply right but at the same width, instead of squishing from the left and right as it does now? \u00a0(I'm not sure how to do this, but I think I can figure it out.)\n<br>\n<br>\n(You're right that I'm misuing blockquote; a reply is not a quote. \u00a0But then it looks ok in non-css browsers.)\n<br>\n<br>\n\"the LessWrong site has explicit threading that's probably more reliable overall -- is it possible to get their threading relationships for their messages?\"\n<br>\n<br>\nI think so, using their API instead of parsing their rss feed. \u00a0Though I don't crosspost there that much, so it might not be worth it.\n<br>\n<br>\n\"A big part of me would love to see what would happen if you didn't group conversations by publication venue and did threading across those boundaries\"\n<br>\n<br>\nI want to do that too, but I can't do it until I update the my server-side API to pull out timestamps for all the sources.</p>", 1342885508], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342885806501", "<p>@<a href=\"https://plus.google.com/105024376133521186824\">Lucas</a>\n\u00a0 \"I just noticed that you've added those 'Top Posts' links on the individual post pages\u2026 how did you implement that?\"\n<br>\n<br>\nI picked ones had a lot of comments, pageviews, and that I liked. \u00a0And then I have some code that picks N random ones to put on each page when I pregenerate the html.</p>", 1342885806], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342889423745", "<p>@<a href=\"https://plus.google.com/105024376133521186824\">Lucas</a>\n\u00a0\"I'm not really thinking of anything that would support AJAX but not CSS.\"\n<br>\n<br>\nHmm. You're right. \u00a0There isn't one. \u00a0That's something I started doing when the site was all static and haven't rethought it. \u00a0Support for non-css browsers doesn't matter here.</p>", 1342889423], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342890051163", "<p>@<a href=\"https://plus.google.com/105024376133521186824\">Lucas</a>\n\u00a0\"That would work well, I think, and shouldn't be too terribly hard.\"\n<br>\n<br>\nI have a max-width set on the containing div, so shifting right of that seems annoying. \u00a0But by only indenting from the left and decreasing the amount of indent I think it can now do a good number of replies without getting too narrow.</p>", 1342890051], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342895405436", "<p>@<a href=\"https://plus.google.com/105024376133521186824\">Lucas</a>\n\u00a0\"A big part of me would love to see what would happen if you didn't group conversations by publication venue and did threading across those boundaries\"\n<br>\n<br>\nDone. \u00a0For example,\u00a0\n<a href=\"http://www.jefftk.com/news/2012-07-17.html#gp-1342651977604\">http://www.jefftk.com/news/2012-07-17.html#gp-1342651977604</a>\n is a google plus reply to\u00a0\n<a href=\"http://www.jefftk.com/news/2012-07-17.html#fb-287020628072239_1319851\">http://www.jefftk.com/news/2012-07-17.html#fb-287020628072239_1319851</a>\n and they nest properly.</p>", 1342895405], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342905423711", "<p>@<a href=\"https://plus.google.com/105024376133521186824\">Lucas</a>\n\u00a0\"it looks like your site is displaying duplicate replies in Google+ conversations\"\n<br>\n<br>\nThis should be fixed now; let me know if you see any more of it.</p>", 1342905423], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342906203674", "<p>@<a href=\"https://plus.google.com/105024376133521186824\">Lucas</a>\n\u00a0\"apply your max-width to those individual containers instead of setting it once on the top-level wrapper\"\n<br>\n<br>\nDone.</p>", 1342906203], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342906308743", "<p>\"my inner markup purist isn't sure about that particular structure of nested blockquotes\"\n<br>\n<br>\nFixed; they're divs now.</p>", 1342906308], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342908208239", "<p>@<a href=\"https://plus.google.com/105024376133521186824\">Lucas</a>\n\u00a0\"I think the time-based stream might not be working quite right across services\"\n<br>\n<br>\nThis should be fixed now. \u00a0I was misusing dateutil.parse and getting my comment as coming at\u00a01342764983 instead of\u00a01342746983, off by five hours. \u00a0(I get an epoch timestamp from g+ but \"2012-07-20T01:16:23+0000\" from fb, so lots of potential for messing things up.)</p>", 1342908208], ["Adam&nbsp;Yie", "https://plus.google.com/114873051319510815414", "gp-1342912289845", "<p>Are you liking the integrated comment streams? Looking at a couple of post I'm finding it tough - context and order disappeared. =\\</p>", 1342912289], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342929614089", "<p>@<a href=\"https://plus.google.com/114873051319510815414\">Adam&nbsp;Yie</a>\n\u00a0\"Are you liking the integrated comment streams? Looking at a couple of post I'm finding it tough - context and order disappeared.\"\n<br>\n<br>\nI'm not sure yet. I want to give it a bit.</p>", 1342929614], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342929761272", "<p>@<a href=\"https://plus.google.com/105024376133521186824\">Lucas</a>\n\u00a0\"I'm interested to see whether this leads the commenters on Jeff's next heavily-discussed post o react and discuss more with folks from the other cross-posted venues\"\n<br>\n<br>\nYes!\n<br>\n<br>\n\"it would be nice to have some sort of indication as to where a comment was posted\"\n<br>\n<br>\nThat would be good. Facebook is blue, reddit is baby blue, lesswrong is green, and google is red, green, blue, and yellow?</p>", 1342929761], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342963177915", "<p>@<a href=\"https://plus.google.com/105024376133521186824\">Lucas</a>\n\u00a0\"Facebook is blue, reddit is baby blue, lesswrong is green, and google is red, green, blue, and yellow?\"\n<br>\n<br>\nI just tried this, and it looked kind of silly:\u00a0\n<a href=\"http://www.jefftk.com/comments_colored_by_service.png\">http://www.jefftk.com/comments_colored_by_service.png</a>\n<br>\n<br>\nInstead I think adding a simple (g+) or (fb) after a comment looks better. \u00a0Trying that for now.</p>", 1342963177], ["Adam&nbsp;Yie", "https://plus.google.com/114873051319510815414", "gp-1342963788447", "<p>@<a href=\"https://plus.google.com/103013777355236494008\">Jeff&nbsp;Kaufman</a>\n\u00a0I don't know the legal restrictions, but what about using the sites' more-or-less standard icons?</p>", 1342963788], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342964196418", "<p>@<a href=\"https://plus.google.com/114873051319510815414\">Adam&nbsp;Yie</a>\n\u00a0\"what about using the sites' more-or-less standard icons?\"\n<br>\n<br>\nI could use icons, though I do like being just text. \u00a0Would that be easier for people to understand?</p>", 1342964196], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342973941392", "<p>@<a href=\"https://plus.google.com/105024376133521186824\">Lucas</a>\n\u00a0\"I was thinking of a color treatment more like ...\"\n<br>\n<br>\nThat does look somewhat better, though red links make me think of pages that don't exist (wikipedia).</p>", 1342973941], ["Adam&nbsp;Yie", "https://plus.google.com/114873051319510815414", "gp-1342976235996", "<p>@<a href=\"https://plus.google.com/105024376133521186824\">Lucas</a>\n\u00a0\n@<a href=\"https://plus.google.com/103013777355236494008\">Jeff&nbsp;Kaufman</a>\n\u00a0\"That does look somewhat better, though red links make me think of pages that don't exist (wikipedia).\"\n<br>\n<br>\nRight, I was suggested the icons since link coloring already has meaning and overloading it again doesn't really appeal to me (because mine\n<br>\nis the only opinion that counts =)).</p>", 1342976235], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1342976934990", "<p>@<a href=\"https://plus.google.com/114873051319510815414\">Adam&nbsp;Yie</a>\n\u00a0\"I was suggested the icons since link coloring already has meaning and overloading it again doesn't really appeal to me\"\n<br>\n<br>\nWhat do you think of the text symbols I have in there now (g+) (fb) compared to icons? \u00a0(I like them not being pictures, but I could see either.)</p>", 1342976934], ["Todd", "https://plus.google.com/112947709146257842066", "gp-1343008375813", "<p>Color the text symbols?</p>", 1343008375]]