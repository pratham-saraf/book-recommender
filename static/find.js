const input = document.querySelector(".finder__input");
const finder = document.querySelector(".finder");
const form = document.querySelector("form");

input.addEventListener("focus", () => {
  finder.classList.add("active");
});

input.addEventListener("blur", () => {
  if (input.value.length === 0) {
    finder.classList.remove("active");
  }
});

form.addEventListener("submit", (ev) => {
  ev.preventDefault();
  finder.classList.add("processing");
  finder.classList.remove("active");
  input.disabled = true;
  setTimeout(() => {
    finder.classList.remove("processing");
    input.disabled = false;
    if (input.value.length > 0) {
      finder.classList.add("active");
    }
  }, 1000);
});

// autocomplete using jquery

$(function() {
  $("#search").autocomplete({
      source : function(request, response) {
          $.ajax({
              type: "POST",
              url : "http://localhost:5000/search",
              dataType : "json",
              cache: false,
              data : {
                  q : request.term
              },
              success : function(data) {
                  console.log(data);
                  const results = document.getElementById("search-results");
                  results.innerHTML = "";
                  loadsuggestions(data);
                  Managelikes();
              },
              error: function(jqXHR, textStatus, errorThrown) {
                  console.log(textStatus + " " + errorThrown);
              }
          });
      },
      minLength : 2
  });
});
//hover hide card



// Render the suggestions
const loadsuggestions = (data) => {
  const results = document.getElementById("search-results");
  const suggestions = []
  const ul = document.createElement("ul");

  data.forEach((item) => {
    const obj = makecard();
    const card = beautifycard(obj, item);
    suggestions.push(card);
  });

  suggestions.forEach((item) => {
    // results.appendChild(item);
    const li = document.createElement("li");
    li.appendChild(item);
    ul.appendChild(li);
  });

  results.appendChild(ul);
};

const makecard = () => {
  const container = document.createElement("article");
  const img = document.createElement("img");
  const book_details = document.createElement("div");
  const like = document.createElement("div");
  const name = document.createElement("h3");
  const publisher = document.createElement("h4");
  const id = document.createElement("h5");
  const link = document.createElement("a");
  return {container, img, book_details, like, name, publisher , link , id};
};

const beautifycard = (obj, item) => {
  const {container, img, book_details, like, name, publisher,link,id} = obj;
  
  container.className="card"

  book_details.className = "book-details";
  like.classList.add("like","unliked");
  name.textContent = `Title - ${item.title}`;
  if (item.publisher) {
  publisher.textContent = `Publisher - ${item.publisher}`;
  } else {
    publisher.textContent = `Publisher - N/A`;
  }
  img.src = item.cover;
  id.textContent = `Goodread Id - ${item.book_id}`;
  link.href = item.url;
  link.setAttribute("target", "_blank");
  link.appendChild(img);

  container.appendChild(link);
  book_details.appendChild(name);
  book_details.appendChild(publisher);
  book_details.appendChild(id);
  container.appendChild(book_details);
  container.appendChild(like);
  return container;
}

// Like the book

const Managelikes = () => {
  const likes = document.querySelectorAll(".like");
  likes.forEach((item) => {
    item.addEventListener("click", (ev) => {
      ev.target.classList.toggle("unliked");
      ev.target.classList.toggle("liked");
      if (ev.target.classList.contains("liked")) {
        console.log("liked");
        favlogfunc(ev.target);
      } else {
        console.log("unliked");
        unfavlogfunc(ev.target);
      }
    });
  });
}

const favlogfunc = (item) => {
  const parent = item.parentElement;
  // const title = parent.querySelector("h3").textContent.split("-")[1].trim();
  const id = parent.querySelector("h5").textContent.split("-")[1].trim();
  $.ajax({
    type: "POST",
    url : "http://localhost:5000/like",
    dataType : "json",
    cache: false,
    data : {
      id: id,
    },
    success : function(data) {
      console.log("added to favs");
    }
  });
}

const unfavlogfunc = (item) => {
  const parent = item.parentElement;
  // const title = parent.querySelector("h3").textContent.split("-")[1].trim();
  const id = parent.querySelector("h5").textContent.split("-")[1].trim();
  $.ajax({
    type: "POST",
    url : "http://localhost:5000/unlike",
    dataType : "json",
    cache: false,
    data : {
      id: id,
    },
    success : function(data) {
      console.log("removed from favs");
    }
  });
}
