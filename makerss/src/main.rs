use regex::Regex;
use std::collections::HashMap;
use std::collections::HashSet;
use std::fs;
use std::io::Write;

const SITE_URL: &str = "https://www.jefftk.com";
const IN_HTML: &str = "news_raw.html";
const FRONT_PAGE: &str = "index.html";
const OUT_DIR: &str = "news2";
const POSTS_DIR: &str = "p2";
const RSS_FNAME: &str = "news2.rss";
const RSS_FULL_FNAME: &str = "news2_full.rss";
const OPENRING_FNAME: &str = "current-openring.html";

const SITE_DIR: &str = "/home/jefftk/jtk";
const SNIPPETS_DIR: &str = "/home/jefftk/code/webscripts/snippets";

const RSS_DESCRIPTION: &str = "Jeff Kaufman's Writing";
const RSS_MAX_POSTS: i32 = 30;
const FRONTPAGE_MAX_POSTS: i32 = 6;
const MAX_UPDATE_CHARS: i32 = 500;
const BREAK_TOKEN: &str = "~~break~~";
const NOTYET_TOKEN: &str = "notyet";
const NOLW_TOKEN: &str = "nolw";

struct Post<'a> {
    title: &'a str,
    slug: &'a str,
    date: &'a str,
    year: u16,
    month: &'a str,
    day: u8,
    tags: Vec<&'a str>,
    services: Vec<&'a str>,
    body: &'a str,
}

fn title_to_url_component(title: &str) -> String {
    let s = title.to_lowercase();
    let s = s.replace("'", "").replace('"', "");
    let s = Regex::new("[^A-Za-z0-9]").unwrap().replace_all(&s, "-");
    let s = Regex::new("-+").unwrap().replace_all(&s, "-");
    let s = Regex::new("^-*").unwrap().replace(&s, "");
    let s = Regex::new("-*$").unwrap().replace(&s, "");
    s.to_string()
}

impl<'a> Post<'a> {
    fn new(title: &'a str, slug: &'a str, date: &'a str, tags: &'a str, body: &'a str) -> Self {
        let date_re: regex::Regex = Regex::new(r"[^ ]* ([^ ]*) (\d*) (\d*).*").unwrap();
        let date_captures = date_re
            .captures(&date)
            .unwrap_or_else(|| panic!("can't parse date '{}'", date));

        let month = date_captures.get(1).unwrap().as_str();
        let day = date_captures.get(2).unwrap().as_str().parse().unwrap();
        let year = date_captures.get(3).unwrap().as_str().parse().unwrap();

        let tag_split_re: regex::Regex = Regex::new(r"[\s\n,]+").unwrap();
        let parsed_tags = tag_split_re.split(&tags).collect::<Vec<&str>>();
        let mut tags = Vec::new();
        let mut services = Vec::new();
        for tag in parsed_tags {
            if tag.contains("/") {
                services.push(tag);
            } else {
                tags.push(tag);
            }
        }        
        Post {
            title,
            slug,
            date,
            year,
            month,
            day,
            tags,
            services,
            body,
        }
    }
}

fn escape(s: &str) -> String {
    s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\"", "&quot;")
}

fn load_snippet(fname: &str) -> String {
    fs::read_to_string(format!("{}/{}", SNIPPETS_DIR, fname)).unwrap()
}

fn write_post(
    post: Post,
    slug_to_title: &HashMap<&str, &str>,
    title_to_next_title: &HashMap<&str, &str>,
    title_to_prev_title: &HashMap<&str, &str>,
) {
    // Write Post HTML
    let title_for_url = title_to_url_component(post.title);

    let post_fname = format!("{}/{}/{}.html", SITE_DIR, POSTS_DIR, title_for_url);

    let mut outf = fs::File::create(post_fname).unwrap();

    let link = [SITE_URL, "p", &title_for_url].join("/");
    let fancy_date = post.date; // TODO
    let tag_block = post.tags.iter().map(|tag| 
        format!("<i><a href='/news/{}'>{}</a></i>", tag, tag)).collect::<Vec<_>>().join(", ");
    write!(outf, "
<!doctype html>
<html lang=en
{}
<script>{}</script>
<script>{}</script>
<style>{}</style>
<title>{}</title>
<div id=wrapper>
{}
<hr>
<div class=content>
<table id='title-date-tags'>
<tr><td valign='top' rowspan='2'><h3><a href='{}'>{}</a></h3></td>
    <td align='right' valign='top'>{}</td></tr>
<tr><td align='right' valign='top'><span>{}</span></td></tr></table>
{}
{}
</div>
<hr>
{}
</div>
",
           load_snippet("gpt_setup.html"),
           load_snippet("google_analytics.js"),
           load_snippet("hover_preview.js"),
           load_snippet("post.css"),
           escape(post.title),
           load_snippet("links.html"),
           link,
           escape(post.title),
           fancy_date,
           tag_block,
           if post.tags.contains(&"notyet") {
               "<p><i>draft post</i></p>"
           } else {
               ""
           },
           post.body.replace(BREAK_TOKEN, ""),
           load_snippet("links.html"),
    ).unwrap();

    // Write to RSS feed
    //todo
}

fn parse_posts(raw: &Vec<u8>) -> Vec<Post> {
    let mut posts: Vec<Post> = Vec::new();

    enum State {
        Before,
        WantSlug,
        WantOpenDiv,
        WantTitle,
        WantTags,
        WantCloseDiv,
    }
    let mut state = State::Before;

    let mut slug = "";
    let mut date = "";
    let mut title = "";
    let mut tags = "";

    let slug_re: regex::Regex = Regex::new("  <a name=\"([^\"]*)\"></a><h3>([^:]*):</h3>").unwrap();
    let title_re: regex::Regex = Regex::new("  <h3>([^<]*)</h3>").unwrap();
    let tags_re: regex::Regex = Regex::new(" *<h4>Tags:[ \n]*([^<]*)</h4>").unwrap();

    let mut line_start = 0;
    let mut tag_start = 0;
    let mut post_start = 0;
    let mut current_line = 0;
    for (i, c) in raw.iter().enumerate() {
        if !c.eq(&b'\n') {
            continue;
        }
        let line_end = i;
        let line = std::str::from_utf8(&raw[line_start..line_end])
            .unwrap_or_else(|_| panic!("not valid utf8 at line {}", current_line));

        match state {
            State::Before => {
                if line.eq("<!-- BEGIN POSTS -->") {
                    state = State::WantSlug;
                }
            }
            State::WantSlug => {
                if let Some(captures) = slug_re.captures(&line) {
                    slug = captures.get(1).unwrap().as_str();
                    date = captures.get(2).unwrap().as_str();
                    state = State::WantOpenDiv;
                }
            }
            State::WantOpenDiv => {
                if line.eq("  <div class=\"pt\">") {
                    state = State::WantTitle;
                }
            }
            State::WantTitle => {
                if let Some(captures) = title_re.captures(&line) {
                    title = captures.get(1).unwrap().as_str();
                    tag_start = line_end + 1;
                    state = State::WantTags;
                }
            }
            State::WantTags => {
                if line.contains("</h4>") {
                    let tags_line = std::str::from_utf8(&raw[tag_start..line_end]).unwrap();
                    let captures = tags_re.captures(tags_line).unwrap_or_else(|| {
                        panic!("can't parse tags '{}' at line {}", tags_line, current_line)
                    });

                    tags = captures.get(1).unwrap().as_str();
                    post_start = line_end + 1;
                    state = State::WantCloseDiv;
                }
            }
            State::WantCloseDiv => {
                if line.eq("  </div>") {
                    let body = std::str::from_utf8(&raw[post_start..line_start]).unwrap();
                    posts.push(Post::new(title, slug, date, tags, body));
                    state = State::WantSlug;
                }
            }
        }
        current_line += 1;
        line_start = line_end + 1;
    }

    posts
}

fn delete_and_recreate_staging() {
    let outdir = [SITE_DIR, OUT_DIR].join("/");
    let postsdir = [SITE_DIR, POSTS_DIR].join("/");

    fs::remove_dir_all(&outdir).expect("unable to remove old out dir");
    fs::create_dir(outdir).expect("unable to create out dir");

    fs::remove_dir_all(&postsdir).expect("unable to remove old posts did");
    fs::create_dir(postsdir).expect("unable to create posts dir");
}

fn main() {
    delete_and_recreate_staging();

    let posts_fname = [SITE_DIR, IN_HTML].join("/");
    let raw = fs::read(posts_fname).expect("Failed to open input");

    let posts = parse_posts(&raw);

    // Set up maps and anything else that requires considering
    // multiple posts at once.
    let mut titles = HashSet::new();
    let mut slug_to_title = HashMap::new();
    let mut title_to_next_title = HashMap::new();
    let mut title_to_prev_title = HashMap::new();
    let mut prev_title = "";
    for post in &posts {
        if titles.contains(post.title) {
            panic!("duplicate title: {}", post.title);
        }
        titles.insert(post.title);

        if slug_to_title.contains_key(post.slug) {
            panic!("duplicate slug: {}", post.slug);
        }
        slug_to_title.insert(post.slug, post.title);

        if !post.tags.contains(&"notyet") {
            if prev_title != "" {
                title_to_next_title.insert(prev_title, post.title);
                title_to_prev_title.insert(post.title, prev_title);
            }

            prev_title = post.title;
        }
    }

    // write_headers();

    // Now write out everything related to each post.
    for post in posts {
        write_post(
            post,
            &slug_to_title,
            &title_to_next_title,
            &title_to_prev_title,
        );
    }

    //write_footers();

    //move_staging_to_prod();
}
