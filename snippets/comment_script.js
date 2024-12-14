var last_visit = document.cookie.replace(/(?:(?:^|.*;\s*)jtk_last_visit\s*\=\s*([^;]*).*$)|^.*$/, "$1");
var current_time = new Date().getTime();
var one_year_gmt_str = new Date(current_time + 31536000000).toGMTString();
document.cookie = "jtk_last_visit=" + current_time +
                          "; path=" + window.location.pathname +
                       "; expires=" + one_year_gmt_str;

function ajaxJsonRequest(url, callback) {
  function createRequestObject() {
    var tmpXmlHttpObject;
    if (window.XMLHttpRequest) {
        // Mozilla, Safari would use this method ...
        tmpXmlHttpObject = new XMLHttpRequest();
    } else if (window.ActiveXObject) {
        // IE would use this method ...
        tmpXmlHttpObject = new ActiveXObject("Microsoft.XMLHTTP");
    }
    return tmpXmlHttpObject;
  }
  var http = createRequestObject();

  //make a connection to the server ... specifying that you intend to make a GET request
  //to the server. Specifiy the page name and the URL parameters to send
  http.open('get', url);
  http.onreadystatechange = function() {
    if(http.readyState == 4){
      callback(JSON.parse(http.responseText));
    }
  }
  http.send(null);
}

all_comments = {};
quote_threshold = 8;
quoting= {}
dictionary = {}

function canonical_wordlist(s) {
  return (s.replace(/&[^ ;]+;/g, '')
           .replace(/<[^> ]+>/g, '')
           .toLowerCase()
           .replace(/[^a-z0-9 ]/g, '')
           .split(" "));
}

function build_phrase_dictionary_for_comment(comment, index) {
  var words = canonical_wordlist(comment);
  for (var i = 0 ; i + quote_threshold < words.length ; i++) {
    var phrase = [];
    for (var j = 0 ; j < quote_threshold ; j++) {
      phrase.push(words[i+j]);
    }
    phrase = phrase.join(" ");
    if (!dictionary[phrase]) {
      dictionary[phrase] = [];
    }
    dictionary[phrase].push(index);
  }
}

function build_phrase_dictionary(comments) {
  dictionary = {}
  for (var i = 0 ; i < comments.length; i++) {
    build_phrase_dictionary_for_comment(comments[i][3], i);
  }
  for (var phrase in dictionary) {
    if (dictionary[phrase].length < 2) {
      delete dictionary[phrase];
    }
  }
}

function find_quotes(comments) {
  build_phrase_dictionary(comments);

  // hash from quoter index to hash from quotee index to first quoted phrase
  var found_quotes = {};

  for (var phrase in dictionary) {
    var indexes = dictionary[phrase];
    var first = indexes[0];
    for (var i = 1 ; i < indexes.length ; i++) {
      var index = indexes[i];
      if (index != first) {
        if (!found_quotes[index]) {
          found_quotes[index] = {};
        }
        if (!found_quotes[index][first]) {
          found_quotes[index][first] = phrase;
        }
      }
    }
  }
  quoting = {};
  not_quoting = {}
  for (var i = 0 ; i < comments.length ; i++) {
    if (found_quotes[i]) {
      var quoted_comments_count = 0;
      var earlier_index = -1;

      // only give comments that quote exactly one earlier comment
      for (var x in found_quotes[i]) {
        quoted_comments_count += 1;
        earlier_index = x;
      }
      if (quoted_comments_count == 1) {
        quoting[i] = earlier_index;
      } else {
        if (!not_quoting[i]) {
          not_quoting[i] = [];
        }
        not_quoting[i].push([earlier_index, quoted_comments_count, found_quotes[i]]);
      }
    }
  }
}

function add_space_for_children(comments) {
  var new_comments = [];
  for (var i = 0 ; i < comments.length ; i++) {
    new_comments[i] = [];
    for (var j = 0 ; j < comments[i].length; j++) {
      new_comments[i].push(comments[i][j]);
    }
    if (new_comments[i].length == 5) {
      // server didn't leave a space for children; add one
      new_comments[i].push([]);
    }
  }
  return new_comments;
}

function nest(comments) {
  find_quotes(comments);
  // iterate backwards to make deletions safe
  for (var i = comments.length - 1 ; i >= 0 ; i--) {
    if (quoting[i]) {
      var earlier_index = quoting[i];
      comments[earlier_index][5].splice(0, 0, comments[i]);
      comments.splice(i,1);
    }
  }

  return comments;
}

function display_posts(comments) {
  return display_posts_helper(nest(comments));
}

function google_plus_color(i) {
  if (i % 6 == 0) {
    return '#004bf5';
  } else if (i % 6 == 1) {
    return '#e61b31';
  } else if (i % 6 == 2) {
    return '#feb90d';
  } else if (i % 6 == 3) {
    return '#004bf5';
  } else if (i % 6 == 4) {
    return '#e61b31';
  } else {
    return '#00930e';
  }
}

function service_abbr(service) {
  if (service == "google plus") {
    return 'g+';
  } else if (service == "lesswrong") {
    return 'lw';
  } else if (service == "the EA Forum") {
    return 'ea';
  } else if (service == "hacker news") {
    return 'hn';
  } else if (service == "facebook") {
    return 'fb';
  } else {
    return service;
  }
}

function friendly_ts(ts) {
  var now = Date.now() / 1000;
  var delta = now - ts;
  if (delta <= 60) {
    return Math.round(delta) + "s";
  }
  delta /= 60;
  if (delta <= 60) {
    return Math.round(delta) + "m";
  }
  delta /= 60;
  if (delta <= 24) {
    return Math.round(delta) + "h";
  }
  delta /= 24;
  if (delta <= 365) {
    if (delta < 45) {
      return Math.round(delta) + "d";
    } else {
      return Math.round(delta/30) + "m";
    }
  }
  delta /= 365;
  if (delta <= 100) {
    return Math.round(delta) + "y";
  }
  delta /= 100;
  return Math.round(delta) + "c";
}

function display_posts_helper(comments) {
  var h = ""
  for (var i = 0; i < comments.length; i++) {
    // h += "<hr>";
    // name, user_link, anchor, message, children
    var name = comments[i][0];
    var user_link = comments[i][1];
    var anchor = comments[i][2];
    var message = comments[i][3];
    var ts = comments[i][4];
    var children = comments[i][5];
    var service = comments[i][6];

    if (message.includes('https://') && !message.includes('<')) {
      message = message.replace(
        /https:\/\/([^ ,!;:]*[^.,!;:])/g,
        '<a href="https://$1">$1</a>');
    }

    h += "<div class=comment id='" + anchor + "' ts=" + ts + ">";
    h += "<a href='" + user_link + "'>" + name + "</a> (";
    if (ts > 1) {
      h += friendly_ts(ts) + ", ";
    }
    h += "via " +  service_abbr(service) + "):";
    h += "<a href='#" + anchor + "' class=commentlink>link</a>";
    h += "<div";
    if (last_visit.length > 0 && ts > last_visit/1000) {
      h += " class=newcomment";
    }
    h += ">";
    h += "<p>" + message + "</p>";
    h += "</div></div>";

    if (children.length > 0) {
      h += "<div class=\"comment-thread\">";
      h += display_posts_helper(children);
      h += "</div>";
    }
  }
  return h;
}

function gotComments(serviceName, response) {
  all_comments[serviceName] = add_space_for_children(response);
  redrawComments();
  if (window.location.hash && window.location.hash.length > 0) {
    var s = window.location.hash;
    window.location.hash = "";
    window.location.hash = s;

    var highlighted_comment = document.getElementById(s.replace('#', ''));
    if (highlighted_comment) {
      highlighted_comment.className += " highlighted";
    }
  }
}

function deep_copy(x) {
  return JSON.parse(JSON.stringify(x));
}

function recursively_add_service(c, service) {
  c.push(service);
  var children = c[5];
  for (var i = 0 ; i < children.length ; i++) {
    recursively_add_service(children[i], service);
  }
}

function all_comments_sorted() {
  var ts_comment = [];
  for (var service in all_comments) {
    for (var i = 0 ; i < all_comments[service].length ; i++) {
      var comment_copy = deep_copy(all_comments[service][i]);
      recursively_add_service(comment_copy, service);
      var ts = comment_copy[4];
      ts_comment.push([ts, comment_copy]);
    }
  }
  ts_comment = ts_comment.sort();
  var c = [];
  for (var i = 0 ; i < ts_comment.length ; i++) {
    c.push(ts_comment[i][1]);
  }
  return c;
}

function redrawComments() {
  var d = document.getElementById("comments");
  var h = "<div class=\"comment-thread\">";
  h += display_posts(all_comments_sorted());
  window.acs = all_comments_sorted();
  window.dictionary = dictionary;
  window.quoting = quoting;
  h += "</div>";
  d.innerHTML=h;
}

function pullComments(wsgiUrl, serviceName) {
  ajaxJsonRequest(wsgiUrl.replace("json-comments", "json-comments-cached"), function(response) {
    gotComments(serviceName, response);
    ajaxJsonRequest(wsgiUrl, function(response) {
      gotComments(serviceName, response);
    });
  });
}
