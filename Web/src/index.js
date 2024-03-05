import { withStyles } from "@material-ui/core/styles";
import { render } from "react-dom";
import React, { useState, useEffect } from "react";
import { ChatFeed, Message } from "react-chat-ui";
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

const muiStyles = {
  form: {
    borderTop: "1px solid black",
    height: "100%",
    display: "flex",
    justifyContent: "space-between",
    padding: "10px"
  },
  container: {
    height: "100vh",
    display: "flex",
    flexDirection: "column",
    padding: "10px"
  },
  chat: {
    height: "95%"
  },
  text: {
    width: "80%",
    height: "100%",
    color:"#1c1111",
    border: "none",
    fontFamily: "Roboto",
    fontSize: "18px"
  },
  sendButton: {
    width: "10%",
    height: "100%",
    backgroundColor: "#fff",
    borderColor: "#1D2129",
    borderStyle: "solid",
    borderRadius: 30,
    borderWidth: 2,
    color: "#1D2129",
    fontWeight: "300"
  }
};
class Chat extends React.Component {
  constructor(props) {
    super(props);
    this.classes = this.props.classes;
    this.state = {
      isTyping: false,
      messages: [
        new Message({
          id: 1,
          message: 'Hi there! I am here to help you to query the Knowldge Graph.',
          senderName: "Auto-KGQA"
        }),
        new Message({
          id: 1,
          message: "Whats is your question?",
          senderName: "Auto-KGQA"
        })
      ],
      currentUser: "You"
    };
  }

  onMessageSubmit(e) {
    const input = this.message;
    e.preventDefault();
    if (!input.value) {
      return false;
    }
    this.pushMessage(0, input.value);
    const query = input.value;
    axios.get('http://0.0.0.0:5000/query/1?query='+query, function (req, res) {
      res.header("Access-Control-Allow-Origin", "*");
    })
    .then(response => {
      const responseData = response.data;
      let answer = responseData.answer;
      // console.log(responseData);
      let pattern = /http\S+/ig;
      if(pattern.test(answer)){
        let matchs = answer.match(pattern);
        console.log(matchs);
        for(const current of matchs){
          let link = current.trim().replaceAll('"',"").replaceAll("'","").replaceAll('<',"").replaceAll('>',"").replaceAll(')',"").trim();
          let link_visualization = "http://localhost:7200/graphs-visualizations?uri=" + encodeURIComponent(link);
          let new_link = '<a target="_blank" href="' + link_visualization + '">'+link+"</a>";
          answer = answer.replaceAll(link,new_link);
        }
      }
      this.pushMessage(1, answer);
      if(responseData.sparql != null && responseData.sparql != "null" && responseData.sparql != ""){
        var query_link = encodeURIComponent(responseData.sparql);
        let content_more_info = 'You can run the SPARQL query directly in the triplestore on the link: <a target="_blank" href="http://localhost:7200/sparql?name=&infer=true&sameAs=true&query='+query_link+'">query</a>';
        content_more_info+= '<span class="feedback_panel">';
        content_more_info+= ' <i title="this answer is correct!" onclick="feedback('+responseData['id']+',1)" class="fa-solid fa-thumbs-up feedback like"></i> <i title="this answer is incorrect!" onclick="feedback('+responseData['id']+',0)" class="fa-solid fa-thumbs-down feedback dislike"></i>';
        content_more_info+='</span>'
      this.pushMessage(1, content_more_info);
      }
    })
    .catch(error => {
      console.error('Error sending request:', error);
    });
    input.value = "";
  }

  pushMessage(recipient = 0, message) {
    const prevState = this.state;
    const newMessage = new Message({
      id: recipient,
      message,
      senderName: "Auto-KGQA"
    });

    prevState.messages.push(newMessage);
    this.setState(this.state);
  }

  render() {
    return (
      <div className={this.classes.container}>
        <div className={this.classes.chat}>
          <ChatFeed
            messages={this.state.messages}
            isTyping={this.state.isTyping}
            showSenderName
            bubbleStyles={{
              text: {
                fontSize: 22,
                color: "black",
              },
              chatbubble: {
                borderRadius: 35,
                padding: 15
              }
            }}
          />
        </div>
        <div style={{ height: "5%", marginBottom: "30px" }}>
          <form
            onSubmit={(e) => this.onMessageSubmit(e)}
            className={this.classes.form}
          >
            <input
              className={this.classes.text}
              ref={(m) => {
                this.message = m;
              }}
              placeholder="Type a message here..."
            />
            <input
              className={this.classes.sendButton}
              type="submit"
              value="Send"
            ></input>
          </form>
        </div>
      </div>
    );
  }
}

const StyleChat = withStyles(muiStyles)(Chat);
render(<StyleChat />, document.getElementById("root"));
