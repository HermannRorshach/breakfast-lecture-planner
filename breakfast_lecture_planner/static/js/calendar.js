document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-schedule-calendar]").forEach((calendar) => {
    const monthSelect = calendar.querySelector("[data-calendar-month]");
    const yearSelect = calendar.querySelector("[data-calendar-year]");
    const week = calendar.querySelector("[data-calendar-week]");
    const previousWeekDays = calendar.querySelector("[data-calendar-week-previous-days]");
    const nextWeekDays = calendar.querySelector("[data-calendar-week-next-days]");
    const schedules = calendar.querySelector("[data-calendar-schedules]");
    const categories = Array.from(calendar.querySelectorAll("[data-calendar-category]"));
    const scheduleUrl = calendar.dataset.scheduleUrl;
    const editIconUrl = calendar.dataset.editIcon;
    const canEdit = calendar.dataset.canEdit === "true";
    const dailyEditorContainer = calendar.querySelector("[data-daily-schedule-editor]");
    const dailyScheduleForm = calendar.querySelector("[data-daily-schedule-form]");
    const dailyScheduleDate = calendar.querySelector("[data-daily-schedule-date]");
    const dailyScheduleError = calendar.querySelector("[data-daily-schedule-error]");
    const scheduleCache = new Map();

    const locale = calendar.dataset.locale || "en";
    const weekdayNames = calendar.dataset.weekdaysShort.split("|");
    const weekdayNamesLong = calendar.dataset.weekdaysLong.split("|");
    const categoryColors = ["#F28C38", "#EB364B", "#50CC2F", "#229191"];
    const scheduleHeaderColors = ["#F2CAA9", "#F6B7B4", "#B4E2A1", "#B3DFF1"];
    const demoSchedules = [
      ["7:50 — „Šrimad-Bhagavatam“ paskaita", "9:30 — Pusryčiai", "11:00 — Sekmadieninė svečių programa", "13:30 — Sekmadieniniai pietūs", "15:00 — Harinama"],
      ["7:50 — Šrilos Prabhupados paskaita", "9:30 — Pusryčiai", "18:00 — Vakaro programa"],
      ["7:50 — „Šrimad-Bhagavatam“ paskaita", "9:30 — Pusryčiai", "18:30 — „Bhagavad-gitos“ skaitiniai"],
      ["7:50 — „Šrimad-Bhagavatam“ paskaita", "9:30 — Pusryčiai", "17:00 — Kirtanų vakaras", "19:00 — Prasadas"],
      ["7:50 — „Šrimad-Bhagavatam“ paskaita", "9:30 — Pusryčiai", "18:30 — Bhakta programa"],
      ["7:50 — „Šrimad-Bhagavatam“ paskaita", "Registracija šeštadienio pietums iki 17:00", "9:30 — Pusryčiai", "18:00 — Vakaro programa"],
      ["7:50 — „Šrimad-Bhagavatam“ paskaita", "9:30 — Pusryčiai", "13:30 — Šeštadienio pietūs", "18:00 — Kirtanas"],
    ];

    let selectedDate = new Date();
    let editingCard = null;
    selectedDate.setHours(12, 0, 0, 0);

    const copyDate = (date) => new Date(date.getFullYear(), date.getMonth(), date.getDate(), 12);
    const shiftedDate = (date, days) => {
      const shifted = copyDate(date);
      shifted.setDate(shifted.getDate() + days);
      return shifted;
    };
    const dateKey = (date) => [
      date.getFullYear(),
      String(date.getMonth() + 1).padStart(2, "0"),
      String(date.getDate()).padStart(2, "0"),
    ].join("-");

    function mondayOf(date) {
      const monday = copyDate(date);
      const day = monday.getDay() || 7;
      monday.setDate(monday.getDate() - day + 1);
      return monday;
    }

    function categoriesFor(date) {
      const seed = date.getDate() + date.getMonth();
      return categories
        .map((category, index) => ({ category, index }))
        .filter(({ index }) => (
          index === seed % categories.length
          || (seed % 3 === 0 && index === (seed + 2) % categories.length)
        ));
    }

    function colorsFor(date, palette) {
      return categoriesFor(date).map(({ index }) => palette[index]);
    }

    function ringPattern(date, fallback = "#d9d3cf") {
      const colors = colorsFor(date, categoryColors);
      if (!colors.length) return `linear-gradient(${fallback}, ${fallback})`;
      if (colors.length === 1) return `linear-gradient(${colors[0]}, ${colors[0]})`;
      const sectorSize = 100 / colors.length;
      const sectors = colors
        .map((color, index) => `${color} ${index * sectorSize}% ${(index + 1) * sectorSize}%`)
        .join(", ");
      return `conic-gradient(from 270deg, ${sectors})`;
    }

    function headerPattern(date, fallback = "#d9d3cf") {
      const colors = colorsFor(date, scheduleHeaderColors);
      if (!colors.length) return `linear-gradient(${fallback}, ${fallback})`;
      if (colors.length === 1) return `linear-gradient(${colors[0]}, ${colors[0]})`;
      const stripeSize = 36;
      const stripes = colors
        .map((color, index) => `${color} ${index * stripeSize}px ${(index + 1) * stripeSize}px`)
        .join(", ");
      return `repeating-linear-gradient(135deg, ${stripes})`;
    }

    function demoContent(date) {
      return demoSchedules[date.getDay()].map((item) => `<p>${item}</p>`).join("");
    }

    async function loadSchedule(date, forceRefresh = false) {
      const key = dateKey(date);
      if (!forceRefresh && scheduleCache.has(key)) return scheduleCache.get(key);
      try {
        const response = await fetch(`${scheduleUrl}?date=${encodeURIComponent(key)}`, {
          cache: "no-store",
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        if (!response.ok) throw new Error("Не удалось загрузить расписание");
        const data = await response.json();
        scheduleCache.set(key, data);
        return data;
      } catch (error) {
        console.error(error);
        return { date: key, content: "", exists: false, error: error.message };
      }
    }

    function createDateButton(date, index, isEdge = false) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "schedule-calendar__date";
      button.dataset.date = dateKey(date);
      button.setAttribute("aria-label", date.toLocaleDateString(locale, { dateStyle: "full" }));
      button.style.setProperty("--date-ring", ringPattern(date));
      const distance = Math.round((date - selectedDate) / 86400000);
      if (!isEdge && distance === 0) button.classList.add("is-selected");
      if (!isEdge && Math.abs(distance) === 1) button.classList.add("is-neighbour");
      button.innerHTML = `
        <span class="schedule-calendar__weekday">${weekdayNames[index % 7]}</span>
        <span class="schedule-calendar__date-number">${date.getDate()}</span>
      `;
      if (!isEdge) {
        button.addEventListener("click", () => {
          selectedDate = copyDate(date);
          render();
        });
      } else {
        button.tabIndex = -1;
      }
      return button;
    }

    function renderWeek() {
      week.replaceChildren();
      previousWeekDays.replaceChildren();
      nextWeekDays.replaceChildren();
      const monday = mondayOf(selectedDate);
      for (let offset = -3; offset < 0; offset += 1) {
        previousWeekDays.append(createDateButton(shiftedDate(monday, offset), offset + 7, true));
      }
      for (let offset = 0; offset < 7; offset += 1) {
        week.append(createDateButton(shiftedDate(monday, offset), offset));
      }
      for (let offset = 7; offset < 10; offset += 1) {
        nextWeekDays.append(createDateButton(shiftedDate(monday, offset), offset % 7, true));
      }
    }

    function refreshExpandButton(card) {
      const body = card.querySelector(".schedule-calendar__schedule-body");
      const button = card.querySelector(".schedule-calendar__schedule-more");
      if (!button || !body) return;
      requestAnimationFrame(() => {
        button.hidden = body.scrollHeight <= body.clientHeight + 1;
      });
    }

    function configureExpandButton(card) {
      const button = card.querySelector(".schedule-calendar__schedule-more");
      if (!button) return;
      refreshExpandButton(card);
      button.addEventListener("click", () => {
        const expanded = card.classList.toggle("is-expanded");
        button.textContent = expanded ? "⌃" : "•••";
        button.setAttribute("aria-expanded", String(expanded));
        button.setAttribute("aria-label", expanded ? "Suskleisti dienos programą" : "Rodyti visą dienos programą");
      });
    }

    async function hydrateScheduleCard(card, date) {
      const data = await loadSchedule(date);
      if (!card.isConnected) return;
      const body = card.querySelector(".schedule-calendar__schedule-body");
      body.innerHTML = data.exists ? data.content : demoContent(date);
      refreshExpandButton(card);
    }

    function waitForDailyEditor() {
      return new Promise((resolve) => {
        let attempts = 0;
        const findEditor = () => {
          const editor = window.editors?.["id_daily-content"];
          if (editor || attempts >= 40) {
            resolve(editor || null);
            return;
          }
          attempts += 1;
          window.setTimeout(findEditor, 50);
        };
        findEditor();
      });
    }

    async function closeDailyEditor() {
      if (!dailyEditorContainer) return;
      dailyEditorContainer.hidden = true;
      dailyScheduleError.hidden = true;
      if (editingCard?.isConnected) {
        editingCard.querySelector(".schedule-calendar__schedule-content").hidden = false;
      }
      schedules.after(dailyEditorContainer);
      editingCard = null;
      await window.scheduleEditLock?.release("daily-schedule");
    }

    async function openDailyEditor(card, date) {
      if (!dailyEditorContainer) return;
      try {
        await window.scheduleEditLock.acquire("daily-schedule");
      } catch (error) {
        alert(error.message);
        return;
      }
      const editor = await waitForDailyEditor();
      if (!editor || !card.isConnected) {
        console.error("CKEditor для дневного расписания не инициализирован");
        await window.scheduleEditLock.release("daily-schedule");
        return;
      }
      const data = await loadSchedule(date, true);
      if (data.error) {
        await window.scheduleEditLock.release("daily-schedule");
        alert(data.error);
        return;
      }
      const body = card.querySelector(".schedule-calendar__schedule-body");
      body.innerHTML = data.exists ? data.content : "";
      editor.setData(data.exists ? data.content : body.innerHTML);
      dailyScheduleDate.value = dateKey(date);
      dailyScheduleError.hidden = true;
      card.querySelector(".schedule-calendar__schedule-content").hidden = true;
      card.querySelector(".schedule-calendar__schedule-header").after(dailyEditorContainer);
      dailyEditorContainer.hidden = false;
      editingCard = card;
      editor.editing.view.focus();
    }

    function createScheduleCard(date, adjacent = false) {
      const article = document.createElement("article");
      article.className = `schedule-calendar__schedule-card${adjacent ? " is-adjacent" : ""}`;
      article.dataset.date = dateKey(date);
      article.style.setProperty("--schedule-header-background", headerPattern(date, "#ded9d5"));
      const editButton = canEdit && !adjacent
        ? `<button class="schedule-calendar__edit-button" type="button" data-daily-schedule-edit aria-label="Редактировать расписание" title="Редактировать"><img src="${editIconUrl}" alt=""></button>`
        : "";
      article.innerHTML = `
        <header class="schedule-calendar__schedule-header">
          <h3>${date.getDate()} d. ${weekdayNamesLong[date.getDay()]}</h3>
          ${editButton}
        </header>
        <div class="schedule-calendar__schedule-content">
          <div class="schedule-calendar__schedule-body">${demoContent(date)}</div>
          ${adjacent ? "" : '<button class="schedule-calendar__schedule-more" type="button" aria-label="Rodyti visą dienos programą" aria-expanded="false">•••</button>'}
        </div>
      `;
      article.querySelector("[data-daily-schedule-edit]")?.addEventListener("click", () => {
        openDailyEditor(article, date);
      });
      hydrateScheduleCard(article, date);
      return article;
    }

    function renderSchedules() {
      if (editingCard) closeDailyEditor();
      const previousCard = createScheduleCard(shiftedDate(selectedDate, -1), true);
      const selectedCard = createScheduleCard(selectedDate);
      const nextCard = createScheduleCard(shiftedDate(selectedDate, 1), true);
      schedules.replaceChildren(previousCard, selectedCard, nextCard);
      configureExpandButton(selectedCard);
    }

    function render() {
      monthSelect.value = String(selectedDate.getMonth());
      yearSelect.value = String(selectedDate.getFullYear());
      renderWeek();
      const activeCategories = categoriesFor(selectedDate).map(({ category }) => category);
      categories.forEach((category) => {
        category.classList.toggle("is-active", activeCategories.includes(category));
      });
      renderSchedules();
    }

    function changeDate(days) {
      selectedDate = shiftedDate(selectedDate, days);
      render();
    }

    dailyScheduleForm?.addEventListener("submit", async (event) => {
      event.preventDefault();
      const submitButton = dailyScheduleForm.querySelector('[type="submit"]');
      submitButton.disabled = true;
      dailyScheduleError.hidden = true;
      try {
        const formData = new FormData(dailyScheduleForm);
        formData.append("edit_lock_token", window.scheduleEditLock.token);
        const response = await fetch(scheduleUrl, {
          method: "POST",
          body: formData,
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Не удалось сохранить расписание");
        scheduleCache.set(data.date, { ...data, exists: true });
        if (editingCard?.isConnected) {
          editingCard.querySelector(".schedule-calendar__schedule-body").innerHTML = data.content;
          refreshExpandButton(editingCard);
        }
        await closeDailyEditor();
        window.notifyScheduleUpdated();
      } catch (error) {
        dailyScheduleError.textContent = error.message;
        dailyScheduleError.hidden = false;
      } finally {
        submitButton.disabled = false;
      }
    });
    calendar.querySelector("[data-daily-schedule-cancel]")?.addEventListener("click", closeDailyEditor);
    calendar.querySelector("[data-calendar-week-previous]").addEventListener("click", () => changeDate(-7));
    calendar.querySelector("[data-calendar-week-next]").addEventListener("click", () => changeDate(7));
    calendar.querySelector("[data-calendar-day-previous]").addEventListener("click", () => changeDate(-1));
    calendar.querySelector("[data-calendar-day-next]").addEventListener("click", () => changeDate(1));
    monthSelect.addEventListener("change", () => {
      selectedDate.setMonth(Number(monthSelect.value), 1);
      render();
    });
    yearSelect.addEventListener("change", () => {
      selectedDate.setFullYear(Number(yearSelect.value));
      render();
    });

    const refreshScheduleData = () => {
      scheduleCache.clear();
      renderSchedules();
    };
    window.addEventListener("schedule-data-updated", refreshScheduleData);
    window.addEventListener("storage", (event) => {
      if (event.key === "schedule-data-updated") refreshScheduleData();
    });

    render();
  });
});
