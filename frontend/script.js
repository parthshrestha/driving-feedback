const guageElement = document.querySelector(".guage");
fetch("https://tbp98oea2e.execute-api.us-east-1.amazonaws.com/dev/rating")
  .then((res) => res.json())
  .then((data) => {
    document.getElementById("rating").textContent = data.average_rating || "N/A";
    console.log(data.average_rating);
    setGuageValue(guageElement, data.average_rating/10);  
     // New: Add feedback messages if available
     if (data.feedback && Array.isArray(data.feedback)) {
      const messages = data.feedback.slice(0, 5); // Only top 5
      const feedbackElements = document.querySelectorAll('.feedback-message');
      
      messages.forEach((msg, index) => {
        if (feedbackElements[index]) {
          feedbackElements[index].textContent = msg || '';
        }
      });
    }
  })
  .catch((err) => {
    console.error("Failed to fetch rating or feedback:", err);
    document.getElementById("rating").textContent = "N/A";
  });


function setGuageValue(guage, value) {
  
  if(value<0 || value>1){
    return;
  } 
  const angle = -(0.5 - value / 2);
  guage.querySelector(".guage_fill").style.transform = `rotate(${angle}turn)`;
  
}
