<template>
  <div class="full-page">
    <div class="content">
      <div class="header">{{ headerText }}</div>
      <textarea v-model="textInput"></textarea>
      <div class="button-group">
        <button class="previous" @click="previous">Previous</button>
        <button class="submit" @click="submitText">Submit</button>
        <button class="next" @click="next">Next</button>
      </div>
      <div class="feedback">{{ feedbackText }}</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      headerText: "Enter some text",
      textInput: "",
      feedbackText: "",
      toCheckSentence: ""
    }
  },
  methods: {
    submitText() {
      // Do something with the text input, for example:
      this.feedbackText = `You submitted: ${this.textInput}`;
    }
  },
  mounted() {
    let currentSentence = 0
    axios.get(`http://127.0.0.1:5000/sentences?lineNumber=${currentSentence}`)
      .then(response => {
        this.headerText = response.data[0];
        this.toCheckSentence = response.data[1];
      })
      .catch(error => {
        console.error(error);
      });
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