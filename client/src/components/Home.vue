<template>
  <div class="panel-container">
    <div class="books-panel">
      <div class="row">
        <RouterLink class="book-item" :to="`/translate/${book.id}`" v-for="book of books">
          <h2 class="book-title">{{ book.title }}</h2>
          <h4 class="author">{{ book.author }}</h4>
          <div class="book-image">
            <img class="book-image" :src="`/covers/${book.slug}.jpg`" />
          </div>
          <div v-if="book.percentage < 100">{{ book.percentage }}%</div>
          <div v-else>Complete</div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>
  
<script>
import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap"
import Popper from "vue3-popper";
import axios from 'axios';
import { useStorage } from '@vueuse/core';
const storage = useStorage('my-store', { currentSentenceIndex: 0 }, localStorage,
  { mergeDefaults: true });

import { ref, onMounted, computed } from 'vue';

export default {
  setup() {
    const books = ref([]);

    const getBookInfos = async () => {
      const result = await axios.get(`/api/books`);
      return result.data;
    };

    onMounted(async () => {
      const bookInfos = await getBookInfos();
      bookInfos.forEach((bookInfo, i) => {
        bookInfo.percentage = 0;
        if (storage.value.bookInformation.length > i) {
          bookInfo.percentage = (((storage.value.bookInformation[i].passedIndexes.length) / bookInfo.numberOfSentences) * 100).toFixed(2);
        }
      });
      books.value = bookInfos;
    })
    return {
      books
    };
  }
}
</script>
  


<style>
.panel-container {
  margin: auto;
}

.book-title {
  height: 80px;
}

.row {
  display: flex;
  flex-flow: row wrap;
  justify-content: center;

}

.author {
  color: gray;
  height: 60px;
}

.books-panel {
  display: flex;
  justify-content: center;
  padding: 50px;
  ;
}

.book-item {
  height: 550px;
  flex-basis: 20%;
  -ms-flex: auto;
  width: 300px;
  position: relative;
  padding: 40px;
  box-sizing: border-box;
  border-radius: 25px;
  border: 2px solid gray;
  margin: 10px;
  text-decoration: none;
  color: inherit;
}

.book-item:hover {
  text-decoration: none;
  color: inherit;
}

.book-image {
  max-width: 200px;
  max-height: 300px;
}

.sentence-token {
  display: inline;
}

.full-page {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.content {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.header {
  font-size: 48px;
  margin-bottom: 20px;
  width: 80%;
}

textarea {
  height: 200px;
  width: 80%;
  margin-bottom: 20px;
}

.button-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 80%;
}

.button-group button {
  font-size: 24px;
  padding: 20px;
}

.previous {
  flex: 0 0 10%;
}

.submit {
  flex: 0 0 76%;
}

.submit-long {
  flex: 0 0 86%;
}

.reveal {
  flex: 0 0 10%;
}

.next {
  flex: 0 0 86%;
}

.next-long {
  flex: 0 0 100%;
}

:root {
  --popper-theme-background-color: #333333;
  --popper-theme-background-color-hover: #333333;
  --popper-theme-text-color: #ffffff;
  --popper-theme-border-width: 0px;
  --popper-theme-border-style: solid;
  --popper-theme-border-radius: 6px;
  --popper-theme-padding: 32px;
  --popper-theme-box-shadow: 0 6px 30px -6px rgba(0, 0, 0, 0.25);
}

.custom-popover {
  font-size: 20pt;
}

.popover-header {
  font-weight: bold;
  margin-bottom: 10px;
}

.token-item {
  cursor: pointer;
}

.token-item:hover {
  color: darkblue;
  text-decoration: underline;
}

.popover-subheader {
  font-size: 10pt;
}

.sentence-part {
  font-size: 16pt;
  font-weight: normal;
}

.answer-text-area {
  font-size: 32px;
  width: 80%;
}

.answer-sentence {
  color: midnightblue;
}

.bi-check-circle-fill {
  color: green;
}

.bi-x-circle-fill {
  color: red;
}

.feedback {
  font-size: 34px;
  padding: 10px;
}

.feedback-icon {
  width: 50px;
  height: 50px;
}

.content {
  font-size: 14px;
}
</style>