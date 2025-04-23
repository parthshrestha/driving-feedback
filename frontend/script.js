fetch("https://tbp98oea2e.execute-api.us-east-1.amazonaws.com/dev/rating")
  .then((res) => res.json())
  .then((data) => {
    document.getElementById("rating").textContent = data.average_rating || "N/A";
  })
  .catch((err) => {
    console.error("Failed to fetch rating:", err);
    document.getElementById("rating").textContent = "N/A";
  });