const guageElement = document.querySelector(".guage");
fetch("https://tbp98oea2e.execute-api.us-east-1.amazonaws.com/dev/rating")
  .then((res) => res.json())
  .then((data) => {
    document.getElementById("rating").textContent = data.average_rating || "N/A";
    console.log(data.average_rating);
    setGuageValue(guageElement, data.average_rating/10);  
  })
  .catch((err) => {
    console.error("Failed to fetch rating:", err);
    document.getElementById("rating").textContent = "N/A";
  });


function setGuageValue(guage, value) {
  
  if(value<0 || value>1){
    return;
  } 
  const angle = -(0.5 - value / 2);
  guage.querySelector(".guage_fill").style.transform = `rotate(${angle}turn)`;
  
}
