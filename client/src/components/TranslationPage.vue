<template>
  <div class="full-page">
    <div class="content">
      <div class="header">
        <div>Book progress: {{ currentIndex + 1 }}/{{ numberOfSentences }}</div>
        <div>Correct sentences: {{ numberPassed }}/{{ numberOfSentences }}</div>
        <div class="sentence-token" v-for="(token, id) of displaySentenceTokenized" :key="id">
          <Popper v-if="!!token.word" class="popper-inner">
            <span class="token-item">{{ token.display }}&nbsp;</span>
            <template #content>
              <div class="custom-popover">
                <div><span class="popover-header">{{ token.word }} <span class="sentence-part">({{ token.definition?.function }})</span></span> </div>
                <div class="popover-body">{{ token.definition?.description }}</div>
                <div class="popover-subheader">Translation from <a target="_blank" :href="token.definition?.link">Deepl</a></div>
                <div class="popover-subheader">For a more detailed definition try <a target="_blank" :href="getLeoLink(token.word)">Leo</a></div>
              </div>
            </template>
          </Popper>
        </div>
        <div class="sentence-token"><a target="_blank" :href="getDeeplSentenceLink()"><img src='/DeeplLogo.svg' /></a></div>
      </div>
      <div v-if="showingAnswer" class="header answer-sentence">  
          <div v-html="getDiffHtml()"></div>
      </div>
      <div class="form-group answer-text-area">
        <textarea class="form-control" v-model="textInput"></textarea> 
      </div>
      <div class="button-group">
        <button v-if="currentIndex !== 0" class="btn btn-primary previous" @click="goToPrevious">Previous</button>
        <button v-if="!showingAnswer" :class="currentIndex === 0 ? 'submit-long' : 'submit'" class="btn btn-success" @click="submitText">Submit</button>
        <button v-if="!showingAnswer" class="btn btn-danger reveal" @click="showAnswer">Show</button>
        <button v-if="showingAnswer" :class="currentIndex === 0 ? 'next-long' : 'next'"  class="btn btn-success " @click="goToNext">Next</button>
      </div>
      <div class="feedback" v-if="feedbackText">
        <span><img  class="feedback-icon" :src='passed ? "/GreenCheck.svg" : "/RedCross.svg"' /></span> {{ feedbackText }}
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
const storage = useStorage('my-store', { currentSentenceIndex: 0, passedIndexes: [] }, localStorage,
  { mergeDefaults: true });

import { ref, onMounted, computed } from 'vue';

export default {
  setup() {
    const displaySentenceTokenized = ref([{
      "definition": null,
      "lemma": null,
      "word": "Enter some text"
    }]);
    const textInput = ref("");
    const feedbackText = ref("");
    const originalSentence = ref("");
    const toCheckSentence = ref("");
    const numberOfSentences = ref(0);
    const bookTitle = ref("");
    const showingAnswer = ref(false);
    const solutionSentence = ref("");
    const passed = ref(false);
    const numberPassed = ref(0);
    const diff = ref([]);



    const submitText = async () => {
      const result = await axios.post(`/api/similarity`, { sentence1: toCheckSentence.value, sentence2: textInput.value });
      console.log(result);
      diff.value = result.data.diff;
      const percentage = result.data.similarity * 100;
      passed.value = percentage > 85;
      const isPassed = passed.value;
      if(isPassed) {
        showingAnswer.value  = true;
        storage.value.passedIndexes.push(storage.value.currentSentenceIndex);
        numberPassed.value = storage.value.passedIndexes.length;
        console.log(numberPassed.value, storage.value.passedIndexes.length, numberOfSentences.value);
      }

      feedbackText.value = `You scored: ${(percentage).toFixed(2)}%`;
    };

    const getDiffHtml = () => {
      return "<span class='diif-word'>" + diff.value.map(token => {
        console.log(token);
        const className = "diff ";
        if (token.startsWith("+")) {
          return "";
        }
        if(token.startsWith("-")) {
          return `<span class="${className}red">${token.substring(1).trim()}</span>`;
        }
        if(token.trim().length === 0) {
          return "</span> <span class='diif-word'>";
        }
        return `<span class="${className}green">${token.trim()}</span>`;
      }).join("") + "</span>";
    };

    const getDiffClass = (token) => {
      const className = "diff ";
      if (token.startsWith("+")) {
        return className + "yellow";
      }
      if(token.startsWith("-")) {
        return className + "red";
      }
      return className + "green";
    };

    const getDiffToken = (baseToken) => {
      if (baseToken.startsWith("+") || baseToken.startsWith("-")) {
        return baseToken.substring(1);
      }
      if(baseToken == " ") {
        //return the html space character
        return "&nbsp;";
      }
      return baseToken; 
    }

    //write a vue3 computed property to return the value of the current index from storage
    const currentIndex = computed(() => {
      return storage.value.currentSentenceIndex;
    });

    const getLeoLink = (word) => {
      return `https://dict.leo.org/german-english/${word}`;
    };

    const getDeeplSentenceLink = () => {
      return `https://www.deepl.com/translator#de/en/${originalSentence.value}`;
    };

    const goToNext = async () => {
      console.log(numberOfSentences.value);
      showingAnswer.value = false;
      if (storage.value.currentSentenceIndex === numberOfSentences.value - 1) {
        return;
      }
      storage.value.currentSentenceIndex = storage.value.currentSentenceIndex + 1;
      fetchSentences();
    };

    const goToPrevious = async () => {
      showingAnswer.value = false;
      if (storage.value.currentSentenceIndex === 0) {
        return;
      }
      storage.value.currentSentenceIndex = storage.value.currentSentenceIndex - 1;
      fetchSentences();
    };

    const showAnswer = () => {
      solutionSentence.value = toCheckSentence.value;
      showingAnswer.value = true;
    };

    const fetchSentences = async () => {
      try {
        textInput.value = "";
        feedbackText.value = "";
        console.log(storage.value.currentSentenceIndex, storage);
        const response = await axios.get(`/api/sentences2?lineNumber=${storage.value.currentSentenceIndex}`);
        console.log(response.data);
        displaySentenceTokenized.value = response.data.presentation_sentence_tokens;
        toCheckSentence.value = response.data.translation;
        originalSentence.value = response.data.sentence;
      } catch (error) {
        console.error(error);
      }
    };

    const getBookInfo = async () => {
      const result = await axios.get(`/api/books`);//todo allow more than one book
      bookTitle.value = result.data[0]["bookTitle"];
      numberOfSentences.value = result.data[0]["numberOfSentences"];
    }

    onMounted(() => {
      getBookInfo()
      fetchSentences();
    });

    return {
      Popper,
      displaySentenceTokenized,
      textInput,
      feedbackText,
      toCheckSentence,
      goToNext,
      goToPrevious,
      numberOfSentences,
      bookTitle,
      submitText,
      showAnswer,
      currentIndex,
      solutionSentence,
      showingAnswer,
      getLeoLink,
      passed,
      getDeeplSentenceLink,
      numberPassed,
      diff,
      getDiffClass,
      getDiffToken,
      getDiffHtml,
    };
  }
}
</script>

<style>
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

textarea.form-control {
  height: 200px;
  margin-bottom: 20px;
  font-size: 40px;
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
.custom-popover{
  font-size: 20pt;
}
.popover-header {
  font-weight: bold;
  margin-bottom: 10px;
}
.token-item{
  cursor: pointer;
}

.token-item:hover{
  color: darkblue;
  text-decoration: underline;
}

.popover-subheader{
  font-size: 10pt;
}

.sentence-part{
  font-size: 16pt;
  font-weight: normal;
}

.answer-text-area{
  font-size: 32px;
  width: 80%;
}

.answer-sentence{
  color: midnightblue;
}

.bi-check-circle-fill{
  color: green;
}

.bi-x-circle-fill{
  color: red;
}

.feedback{
  font-size: 34px;
  padding: 10px;
}
.feedback-icon{
  width: 50px;
  height: 50px;
}

.content{
  font-size: 14px;
}
.green{
  color: green;
}
.red{
  color: red;
}
.yellow{
  color: yellow;
}
.diff{
  width: min-content;
  padding: 0%;
  margin: 0%;
  white-space: normal;
}
.answer-sentence{
  width: 80%;
}
</style>