[["Ariel", "https://plus.google.com/113667834513475506190", "gp-1321363500245", "<p>Truly deionized water actually doesn't conduct electricity (its resistivity is ~18 megaohm-cm).  Tap water, on the other hand, has all sorts of ions in it, which is what enables it to conduct (resistivity is far lower at roughly 1 Kohm-cm).  So, yes, it's different in saltwater.  Dangerous distance from the power cord is determined by resistivity and also the voltage of the line as it's the current going through your body that actually hurts you and you can assume a roughly ohmic system (for the purposes of figuring out if you'll die, anyway).  I'd imagine that the important distance is the shortest linear distance between your body and the end of the wire, although grounding might have something to do with it.  AC and DC are different in terms of electric shocks because AC basically paralyzes you, meaning you can't get away and a lot more damage is done.  So in general it's more dangerous than DC at the same voltage/current.</p>", 1321363500], ["Elmo", "https://plus.google.com/114274595318045509956", "gp-1321372731308", "<p>@Ariel It is DC that will paralyse you and AC that is safer.  Hence one of the reasons we have AC for household supplies.</p>", 1321372731], ["Ariel", "https://plus.google.com/113667834513475506190", "gp-1321373405729", "<p>@<a href=\"https://plus.google.com/114274595318045509956\">Elmo</a>\n , I think you're mistaken.  DC causes a single violent muscle contraction, which normally causes the victim to fall away from the source.  AC produces continuous contractions (apparently known as tetany), which freezes the victim in contact with the source.  (Cf. \n<a href=\"http://www.medscape.com/viewarticle/410681_3\">http://www.medscape.com/viewarticle/410681_3</a>\n, \n<a href=\"http://www.uic.edu/labs/lightninginjury/treatment.html\">http://www.uic.edu/labs/lightninginjury/treatment.html</a>\n).  In my understanding, we use AC for domestic supply as it can be transmitted at high voltage and delivered at low voltage, whereas DC would have to be delivered at high voltage to minimize transfer losses (this does affect the safety concerns, but in a different way).</p>", 1321373405], ["Alex", "https://plus.google.com/100936518160252317727", "gp-1321375240246", "<p>You're both right and wrong. They can both kill you, given enough current (and household power supplies plenty either way). Edison killed an elephant with AC as a parlor trick (see \n<a href=\"http://en.wikipedia.org/wiki/War_of_Currents\">http://en.wikipedia.org/wiki/War_of_Currents</a>\n); DC meanwhile transmits more power per volt, and so is plenty dangerous too.\n<br>\n<br>\nThe reason we have AC today is it's far easier and more efficient to convert between voltages using AC. This enables high-voltage, high-efficiency long-distance AC wires.\n<br>\n<br>\nTo answer the original question: it really depends, and is complicated by all sorts of things. If you stick one hand in electrified water, you may get a nasty shock, but you probably won't die. It's far worse if the current manages to go through your heart. In regular tap water, your body is lower resistance than the water, so the current will flow through you (bad news) rather than just going straight from wire to wire. This means you may actually be safer in saltwater, since the water might be more conductive than you are. Electricity likes to follow the path of least resistance.\n<br>\n<br>\nAlso worth mentioning is that wet hands are almost as dangerous as a bathtub. Normally your skin is a pretty good insulator, but if your hands are wet, conductivity skyrockets. And of course it's all highly nonlinear.</p>", 1321375240], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1321377686005", "<p>So how far from a downed power line can you safely swim?</p>", 1321377686], ["Alex", "https://plus.google.com/100936518160252317727", "gp-1321380431294", "<p>Not sure. I don't even know if you could realistically model that with any hope of precision. It would depend on the ion content of the water, your body's resistivity, the resistance of the interfaces between wire and water, and water and body, and of course the voltage of the downed power line. But let's try.\n<br>\n<br>\nLet's suppose, for the sake of conservativeness, that we use Ariel's resistivity figure of 1kOhm-cm for water (=10 Ohm-m), that your body is a perfect conductor, and that the hot and cold leads are on opposite sides of your body, so that the current flows through your heart. 70mA is sufficient to kill in this case. Also assume that this is a typical rural distribution pole, rather than a high-voltage long-distance transmission line. They typically carry electricity at 7.2kV. Doing some math:\n<br>\n<br>\nR = V / I\n<br>\nV = 7200 V\n<br>\nI = 0.07 A\n<br>\nso desired R = 102,900 Ohm = 103kOhm\n<br>\n<br>\nNow, to convert resistance into resistivity, we need to use the formula\n<br>\nrho = R * A / L, where\n<br>\nrho is the resistivity,\n<br>\nR is the resistance,\n<br>\nA is the surface area of an end of a solid resistor made of the material, and\n<br>\nL is the length of that material. (\n<a href=\"http://en.wikipedia.org/wiki/Electrical_resistivity_and_conductivity\">http://en.wikipedia.org/wiki/Electrical_resistivity_and_conductivity</a>\n)\n<br>\n<br>\nAssume the surface area is, oh I don't know, 1/3 the average surface area of a male human body (remember, this is the cross-section of the volume between the wire and your body), so 0.6 m^2 (\n<a href=\"http://en.wikipedia.org/wiki/Body_surface_area\">http://en.wikipedia.org/wiki/Body_surface_area</a>\n). Then\n<br>\nL = R * A / rho\n<br>\n(103000 Ohm) (0.6 m^2) / (10 Ohm-m) = 6180 m\n<br>\n<br>\nThat sounds, err, rather high to me, though. Hopefully the breaker would trip before electrocuting all the fish in all the lakes on this side of the earth.</p>", 1321380431], ["Jeff&nbsp;Kaufman", "https://plus.google.com/103013777355236494008", "gp-1321380689101", "<p>@<a href=\"https://plus.google.com/100936518160252317727\">Alex</a>\n \"that the hot and cold leads are on opposite sides of your body\"\n<br>\n<br>\nIs that likely?  I was thinking that if a broken power line fell in to a pond then the hot and cold leads would be right next to each other.</p>", 1321380689], ["Alex", "https://plus.google.com/100936518160252317727", "gp-1321381282126", "<p>I think it's not particularly probable. But we have to start assuming somewhere...\n<br>\n<br>\nOkay, let's try and tweak this. Say the wires fall near each other, say 1m apart at their closest. Let's also assume the water is uniformly conductive. Since the wire is far more conductive than the water ever will be, if no other conductors are present then current will flow between these two closest points, not anywhere else. In this case, in order for current to flow through your body, you would need to provide a shorter path than the 1m of water.\n<br>\n<br>\nThe distance from hot wire to one part of your body, plus the distance from some other part of your body to the cold wire, would have to be less than 1m. The furthest you could be from the nearer wire in order for this to hold would be 0.5m. A much more sensible number. The key is that current follows the path of least resistance; if you provide that path, then you get zapped.</p>", 1321381282], ["Alex", "https://plus.google.com/100936518160252317727", "gp-1321381496591", "<p>It's worth pointing out that water is not uniformly conductive; that the wires might get some mud or whatever on them that electrically insulates them from water; that every barrier between different materials has some resistance, so touching a wire is different from being near it; and, perhaps most importantly, that wires are hard to spot at the bottom of a lake, so you'd want to be pretty darn sure you're not near a stray strand.</p>", 1321381496], ["Alex", "https://plus.google.com/100936518160252317727", "gp-1321385307344", "<p>Okay, okay, you got me, I was simplifying. Most transmission lines carry three-phase power, which is then converted to single-phase near the customer. In the US there's not typically a ground return, and single-phase is derived by simply connecting across two of the phases and running the result through a transformer. But if we are following the second argument, where the wires are near each other, it doesn't really matter. If you are the path of least resistance, you will almost certainly die, end of story. 1 meter of water is not enough to insulate you from anywhere near that much voltage.</p>", 1321385307]]