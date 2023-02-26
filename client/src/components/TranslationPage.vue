<template>
  <div class="full-page">
    <div class="content">
      <div class="header">{{ headerText }}</div>
      <textarea v-model="textInput"></textarea>
      <div class="button-group">
        <button class="previous" @click="goToPrevious">Previous</button>
        <button class="submit" @click="submitText">Submit</button>
        <button class="next" @click="goToNext">Next</button>
      </div>
      <div class="feedback">{{ feedbackText }}</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useStorage } from '@vueuse/core';
const storage = useStorage('my-store', { currentSentenceIndex: 0 }, localStorage,
  { mergeDefaults: true });

import { ref, onMounted } from 'vue';

export default {
  setup() {
    const headerText = ref("Enter some text");
    const textInput = ref("");
    const feedbackText = ref("");
    const toCheckSentence = ref("");
    const numberOfSentences = ref(0);
    const bookTitle = ref("");

    const submitText = async () => {
      const result = await axios.post(`http://127.0.0.1:5000/similarity`, { sentence1: toCheckSentence.value, sentence2: textInput.value });
      console.log(result);

      feedbackText.value = `You scored: ${(result.data.similarity * 100).toFixed(2)}%`;
    };

    const goToNext = async () => {
      console.log(numberOfSentences.value);
      if(storage.value.currentSentenceIndex === numberOfSentences.value - 1){
        return;
      }
      storage.value.currentSentenceIndex = storage.value.currentSentenceIndex + 1;
      fetchSentences();
    };

    const goToPrevious = async () => {
      if(storage.value.currentSentenceIndex === 0){
        return;
      }
      storage.value.currentSentenceIndex = storage.value.currentSentenceIndex - 1;
      fetchSentences();
    };

    const fetchSentences = async () => {
      try {
        textInput.value = "";
        feedbackText.value = "";
        console.log(storage.value.currentSentenceIndex, storage);
        const response = await axios.get(`http://127.0.0.1:5000/sentences?lineNumber=${storage.value.currentSentenceIndex}`);
        headerText.value = response.data[0];
        toCheckSentence.value = response.data[1];
      } catch (error) {
        console.error(error);
      }
    };

    const getBookInfo = async () => {
      const result = await axios.get(`http://127.0.0.1:5000/bookInfo`);//todo allow more than one book
      bookTitle.value = result.data["bookTitle"];
      numberOfSentences.value = result.data["numberOfSentences"];
    }

    onMounted(() => {
      getBookInfo()
      fetchSentences();
    });

    return {
      headerText,
      textInput,
      feedbackText,
      toCheckSentence,
      goToNext,
      goToPrevious,
      numberOfSentences,
      bookTitle,
      submitText
    };
  }
}
</script>

<style>
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
  margin: 0 1%;
}

.previous {
  flex: 0 0 10%;
}

.submit {
  flex: 0 0 76%;
}

.next {
  flex: 0 0 10%;
}
</style>