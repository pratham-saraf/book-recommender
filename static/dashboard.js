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
      // dataType : "json",
      cache: false,
      data : {
        id: id,
      },
      success : function(data) {
        console.log("added to favs");
      },
      error : function(data) {
        console.log("error");
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
      // dataType : "json",
      cache: false,
      data : {
        id: id,
      },
      success : function(data) {
        console.log("removed from favs");
        location.reload();
      },
      error : function(data) {
        console.log("error");
        
      }
    });
  }
  
Managelikes();