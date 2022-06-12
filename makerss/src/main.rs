use regex::Regex;
use std::collections::HashMap;
use std::collections::HashSet;
use std::fs;

//const SITE_URL: &str = "https://www.jefftk.com";
const SITE_DIR: &str = "/home/jefftk/jtk";
const IN_HTML: &str = "news_raw.html";

struct Post<'a> {
    title: &'a str,
    slug: &'a str,
    date: &'a str,
    year: u16,
    month: &'a str,
    day: u8,
    tags: Vec<&'a str>,
    body: &'a str,
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

        let tag_split_re: regex::Regex = Regex::new(r"[\s\n,]*").unwrap();
        let parsed_tags = tag_split_re.split(&tags).collect::<Vec<&str>>();

        Post {
            title,
            slug,
            date,
            year,
            month,
            day,
            tags: parsed_tags,
            body,
        }
    }
}

fn write_post(
    post: Post,
    slug_to_title: &HashMap<&str, &str>,
    title_to_next_title: &HashMap<&str, &str>,
    title_to_prev_title: &HashMap<&str, &str>,
) {
    // Write Post HTML

    // Write to RSS feed
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
        line_start = line_end + 1;

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
                    tag_start = line_start;
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
                    post_start = line_start;
                    state = State::WantCloseDiv;
                }
            }
            State::WantCloseDiv => {
                if line.eq("  </div>") {
                    let body = std::str::from_utf8(&raw[post_start..line_end]).unwrap();
                    posts.push(Post::new(title, slug, date, tags, body));
                    state = State::WantSlug;
                }
            }
        }
        current_line += 1;
    }

    posts
}

fn main() {
    // delete_staging()
    // make_staging()

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
