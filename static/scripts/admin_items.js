document.addEventListener("DOMContentLoaded", function() {
    const lang = document.documentElement.lang || "da";
  
    document.querySelectorAll('.created-at').forEach(function(el) {
      const ts = parseInt(el.textContent, 10);
      if (!isNaN(ts)) {
        const date = new Date(ts * 1000);
        let options;
  
        if (lang === "en") {
          options = { month: '2-digit', day: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' };
          el.textContent = date.toLocaleString('en-US', options);
        } else {
          options = { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' };
          el.textContent = date.toLocaleString('da-DK', options);
        }
      } else {
        el.textContent = "-";
      }
    });
  });
  