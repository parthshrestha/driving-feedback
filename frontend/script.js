const guageElement = document.querySelector(".guage");
let currentIndex = 0;
let feedbackMessages = [];

fetch("https://nayadriver.com/rating.json", {
  cache: "force-cache"
})
  .then((res) => res.json())
  .then((data) => {
    applyRatingAndFeedback(data);
  })
  .catch((err) => {
    console.error("Failed to load snapshot:", err);
  });

function applyRatingAndFeedback(data) {
  document.getElementById("rating").textContent = data.average_rating || "N/A";
  setGuageValue(guageElement, (data.average_rating || 0) / 10);

  if (Array.isArray(data.feedback)) {
    feedbackMessages = data.feedback;
    startScrollingFeedback();
  }
}

function setGuageValue(guage, value) {
  if (value < 0 || value > 1) return;
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
