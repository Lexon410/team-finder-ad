// Project-specific JS (complete project action + toggle participate)
(function(){
  document.addEventListener("DOMContentLoaded", function() {
    // 1. Завершение проекта
    const completeBtn = document.getElementById("complete-project-btn");
    if (completeBtn) {
      completeBtn.addEventListener("click", function(e) {
        e.preventDefault();
        const projectId = completeBtn.dataset.id;
        if (!projectId) return;

        fetch(`/projects/${projectId}/complete/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": window.getCookie ? window.getCookie("csrftoken") : "",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
          if (data.status === "ok") {
            const statusEl = document.querySelector(".project-status-black");
            if (statusEl) statusEl.textContent = "Закрыт";
            completeBtn.remove();
            if (window.toast) window.toast("Проект завершён", { type: 'info' });
            else alert("Проект завершён");
          } else {
            if (window.toast) window.toast("Ошибка при завершении проекта", { type: 'error' });
            else alert("Ошибка при завершении проекта");
          }
        })
        .catch(err => {
          console.error("Ошибка запроса:", err);
          if (window.toast) window.toast("Ошибка сети", { type: 'error' });
          else alert("Ошибка сети");
        });
      });
    }

    // 2. Участие в проекте
    const participateBtn = document.getElementById("participate-btn");
    if (!participateBtn) return;

    const participantsList = document.getElementById("participants-list");
    const participantsCount = document.getElementById("participants-count");
    if (!participantsList || !participantsCount) return;

    const userId = participateBtn.dataset.userId;
    const projectId = participateBtn.dataset.project;
    const userName = participateBtn.dataset.userName || "";
    const userAvatar = participateBtn.dataset.userAvatar || "";

    function updateUI(participating) {
      if (participating) {
        participateBtn.textContent = "Отказаться от участия";
        const noParticipants = document.getElementById("no-participants");
        if (noParticipants) noParticipants.remove();

        const a = document.createElement("a");
        a.href = `/users/${userId}`;
        a.id = `participant-${userId}`;
        a.innerHTML = `
          <div class="participant-item">
            <img src="${userAvatar}" alt="Аватар" class="participant-avatar">
            <div class="participant-info">
              <span class="participant-name">${userName}</span>
              <span class="participant-role">Участник</span>
            </div>
          </div>
        `;
        participantsList.appendChild(a);
        const currentCount = parseInt(participantsCount.textContent);
        participantsCount.textContent = currentCount + 1;
      } else {
        participateBtn.textContent = "Участвовать";
        const el = document.getElementById(`participant-${userId}`);
        if (el) el.remove();
        let currentCount = parseInt(participantsCount.textContent);
        if (currentCount > 0) {
          participantsCount.textContent = currentCount - 1;
        }
        if (parseInt(participantsCount.textContent) === 0) {
          const p = document.createElement("p");
          p.id = "no-participants";
          p.textContent = "Пока нет участников";
          participantsList.appendChild(p);
        }
      }
    }

    participateBtn.addEventListener("click", function(e) {
      e.preventDefault();
      if (!projectId) return;

      fetch(`/projects/${projectId}/toggle-participate/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": window.getCookie ? window.getCookie("csrftoken") : "",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({})
      })
      .then(resp => {
        if (!resp.ok) throw new Error('Network response was not ok');
        return resp.json();
      })
      .then(data => {
        if (data.status !== "ok") {
          alert("Ошибка при изменении участия");
          return;
        }
        updateUI(data.participating);
      })
      .catch(err => {
        console.error("Ошибка запроса:", err);
        alert("Ошибка сети при изменении участия");
      });
    });
  });
})();