let pagination1;
let pagination2;
let current_category = 1;
let current_limit = 10;

document.addEventListener("DOMContentLoaded", function () {
    pagination1 = document.querySelectorAll('.pagination')[0];
    pagination2 = document.querySelectorAll('.pagination')[1];

    fetchData();
});

function fetchData(page=null, limit = null) {
    let url = new URL("/forum/messages", window.location.origin);
    const forumContainer = document.getElementById("forum-container");

    const topicId = forumContainer.getAttribute("data-topic-id");
    url.searchParams.append("topic_id", topicId);
    if (page !== null) url.searchParams.append("page", page);
    if (limit !== null) url.searchParams.append("limit", limit);

    fetch(url)
        .then(response => response.json())
        .then(data => {
            populateArticles(data.messages);
            console.log(data.pages);
            populatePagination(pagination1, data.pages, 1);
            populatePagination(pagination2, data.pages, 1);
        })
        .catch(error => console.error("Error fetching articles:", error));
}

function populateArticles(articles) {
    const container = document.querySelector(".forum-articles");
    container.innerHTML =`
        <div class="articles-header">
            <span class="column-title">Title</span>
            <span class="column-author">Author</span>
            <span class="column-date">Creation Date</span>
            <span class="column-replies">Replies</span>
            <span class="column-last-message">Last Message</span>
        </div>`;

    console.log(articles);
    articles.forEach(article => {
        const articleRow = document.createElement("div");
        articleRow.classList.add("article-row");
        articleRow.innerHTML =`
            <span class="article-title">${article.message}</span>
            <span class="article-author">${article.author}</span>
            <span class="article-date">${article.creationDate}</span>
            <span class="article-replies">${article.replies}</span>
            <span class="article-last-message">${article.lastMessage}</span>`
        ;
        container.appendChild(articleRow);
    });
}

function populatePagination(container, totalPages, currentPage) {
    console.log(container);
    const pageNumbersContainer = container.querySelector('.page-numbers');
    const firstPageButton = container.querySelector('.first-page');
    const prevPageButton = container.querySelector('.prev-page');
    const nextPageButton = container.querySelector('.next-page');
    const lastPageButton = container.querySelector('.last-page');

    // Clear existing page numbers
    pageNumbersContainer.innerHTML = '';

    // Create page number buttons
    for (let i = 1; i <= totalPages; i++) {
        const pageButton = document.createElement('button');
        pageButton.classList.add('page-number');
        pageButton.textContent = i;
        if (i === currentPage) {
            pageButton.classList.add('active'); // Highlight current page
        }

        pageButton.addEventListener('click', () => { fetchData(current_category, i, current_limit); });

        pageNumbersContainer.appendChild(pageButton);
    }

    firstPageButton.onclick = () => fetchData(current_category, 1, current_limit);
    prevPageButton.onclick = () => fetchData(current_category, Math.max(1, currentPage - 1), current_limit);
    nextPageButton.onclick = () => fetchData(current_category, Math.min(totalPages, currentPage + 1), current_limit);
    lastPageButton.onclick = () => fetchData(current_category, totalPages, current_limit);

    // Disable or enable pagination buttons based on current page
    firstPageButton.classList.toggle("disabled", currentPage === 1);
    prevPageButton.classList.toggle("disabled", currentPage === 1);
    nextPageButton.classList.toggle("disabled", currentPage === totalPages);
    lastPageButton.classList.toggle("disabled", currentPage === totalPages);
}
