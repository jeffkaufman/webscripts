use regex::Regex;
use std::fs::File;
use std::io::{self, BufRead};

//const SITE_URL: &str = "https://www.jefftk.com";
const SITE_DIR: &str = "/home/jefftk/jtk";
const IN_HTML: &str = "news_raw.html";

fn handle_post(slug: &str, date: &str, title: &str, tags: &str) {
    println!("would handle post: {} {} {} {}", slug, date, title, tags);
}

fn parse_posts() {
    enum State {
        Before,
        WantSlug,
        WantOpenDiv,
        WantTitle,
        WantTags,
        WantCloseDiv,
    }

    let posts_fname = [SITE_DIR, IN_HTML].join("/");
    let file = File::open(posts_fname).expect("Failed to open input");

    let mut state = State::Before;
    let mut post: Vec<String> = Vec::new();
    let mut tag_lines: Vec<String> = Vec::new();

    let slug_re = Regex::new("  <a name=\"([^\"]*)\"></a><h3>([^:]*):</h3>").unwrap();
    let title_re = Regex::new("  <h3>([^<]*)</h3>").unwrap();
    let tag_re = Regex::new("  <h4>Tags: ([^<]*)</h4>").unwrap();

    let mut slug = String::new();
    let mut date = String::new();
    let mut title = String::new();
    let mut tags = String::new();

    for line in io::BufReader::new(file).lines() {
        let line = line.expect("Failed to read line");

        match state {
            State::Before => {
                if line.eq("<!-- BEGIN POSTS -->") {
                    state = State::WantSlug;
                }
            }
            State::WantSlug => {
                if let Some(captures) = slug_re.captures(&line) {
                    slug = (&captures[1]).to_string();
                    date = (&captures[2]).to_string();
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
                    title = (&captures[1]).to_string();
                    state = State::WantTags;
                }
            }
            State::WantTags => {
                tag_lines.push(line);
                if let Some(captures) = tag_re.captures(&tag_lines.join(" ")) {
                    tags = (&captures[1]).to_string();
                    tag_lines.clear();
                    state = State::WantCloseDiv;
                }
            }
            State::WantCloseDiv => {
                if line.eq("  </div>") {
                    handle_post(&slug, &date, &title, &tags);
                    post.clear();
                    state = State::WantSlug;
                } else {
                    post.push(line);
                }
            }
        }
    }
}

fn main() {
    // delete_old_staging
    // make_new_staging
    parse_posts();
}
