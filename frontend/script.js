

  const guageElement = document.querySelector(".guage");
  let currentIndex = 0;
  let feedbackMessages = [];

  fetch("https://tbp98oea2e.execute-api.us-east-1.amazonaws.com/dev/rating")
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("rating").textContent = data.average_rating || "N/A";
      console.log("Fetched data:", data);
      setGuageValue(guageElement, data.average_rating/10);  

      if (data.feedback && Array.isArray(data.feedback)) {
        feedbackMessages = data.feedback;
        startScrollingFeedback();
      }
    })
    .catch((err) => {
      console.error("Failed to fetch rating or feedback:", err);
      document.getElementById("rating").textContent = "N/A";
    });

  function setGuageValue(guage, value) {
    if (value < 0 || value > 1) {
      return;
    } 
    const angle = -(0.5 - value / 2);
    guage.querySelector(".guage_fill").style.transform = `rotate(${angle}turn)`;
  }

  function startScrollingFeedback() {
    const container = document.querySelector('.feedback-container');
    const feedbackElements = container.querySelectorAll('.feedback-message');

    updateFeedbackMessages();

    setInterval(() => {
      currentIndex++;
      updateFeedbackMessages();
    }, 3000);
  }

  function updateFeedbackMessages() {
    const feedbackElements = document.querySelectorAll('.feedback-message');
  
    feedbackElements.forEach((element, i) => {
      const feedbackItem = feedbackMessages[(currentIndex + i) % feedbackMessages.length];
  
      if (feedbackItem) {
        const ratingOutOf5 = Math.round(feedbackItem.rating / 2);
        const fullStars = "★".repeat(ratingOutOf5);
        const emptyStars = "☆".repeat(5 - ratingOutOf5);
        const stars = `${fullStars}${emptyStars}`;
  
        element.innerHTML = `<span class="stars">${stars}</span> <span class="comment">${feedbackItem.comment}</span>`;
      } else {
        element.textContent = "";
      }
  
      element.style.opacity = 1 - (i * 0.2);
      element.style.transform = `translateY(${i * 30}px)`;
    });
  }
  


