import { withStyles } from "@material-ui/core/styles";
import { render } from "react-dom";
import React, { useState, useEffect } from "react";
import { ChatFeed, Message } from "react-chat-ui";
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Cookies from 'universal-cookie';
var showdown  = require('showdown')

var converter = new showdown.Converter();
function parseMD(md){
  // console.log(responseData);
  // let pattern = /http\S+/ig;
  // if(pattern.test(answer)){
    //   let matchs = answer.match(pattern);
    //   console.log(matchs);
    //   matchs.sort((a, b) => b.length - a.length);
    //   for(const current of matchs){
      //     let link = current.trim().replaceAll('"',"").replaceAll("'","").replaceAll('<',"").replaceAll('>',"").replaceAll(')',"").trim();
      //     let link_visualization = "http://localhost:7200/graphs-visualizations?uri=" + encodeURIComponent(link);
      //     let new_link = '<a target="_blank" href="' + link_visualization + '">'+link+"</a>";
      //     answer = answer.replaceAll(link,new_link);
      //   }
      // }
      
      let htmlT = converter.makeHtml(md);
      htmlT = htmlT.replaceAll("<a ",'<a target="_blank" ');
      return htmlT;
    }
    
// const text = "John, also known as John Doe ([http://www.example.lirb.com/JohnDoe](http://www.example.lirb.com/JohnDoe)) or simply Jonny, is a 25-year-old software engineer. He was born on January 1, 1998, and he is a living being and a person. He is considered a resource and a thing in web ontology records. He's known by other individuals such as Jane ([http://www.example.lirb.com/Jane](http://www.example.lirb.com/Jane)), Tom ([http://www.example.lirb.com/Tom](http://www.example.lirb.com/Tom)), Jack Smith ([http://www.example.lirb.com/JackSmith](http://www.example.lirb.com/JackSmith)), and someone referred to as 'Someone' ([http://www.example.lirb.com/SomeOne](http://www.example.lirb.com/SomeOne)). He works at ‘JohnDoeWork’([http://www.example.lirb.com/JohnDoeWork](http://www.example.lirb.com/JohnDoeWork)). More information is available in the timeline object ([http://www.example.lirb.com/Timeline/JohnDoe](http://www.example.lirb.com/Timeline/JohnDoe), [http://www.example.lirb.com/Timeline/John](http://www.example.lirb.com/Timeline/John)). Here is his thumbnail profile: [https://cdn-icons-png.flaticon.com/512/10/10522.png](https://cdn-icons-png.flaticon.com/512/10/10522.png).";
// console.log(parseMD(text));


const cookies = new Cookies();

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
    this.user_id = this.props.user_id;
    // console.log("user_id configurado na classe:"+this.user_id);
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
    this.state.isTyping = true;
    this.setState(this.state);
    e.preventDefault();
    if (!input.value) {
      return false;
    }
    this.pushMessage(0, input.value);
    const query = input.value;
    // console.log("vai consultas com user_id:"+this.user_id);
    axios.get('http://0.0.0.0:5000/query/'+this.user_id+'?query='+query, function (req, res) {
      res.header("Access-Control-Allow-Origin", "*");
    })
    .then(response => {
      const responseData = response.data;
      let answer = responseData.answer;
      answer = parseMD(answer);
      this.pushMessage(1, answer);
      if(responseData.sparql != null && responseData.sparql != "null" && responseData.sparql != ""){
        var query_link = encodeURIComponent(responseData.sparql);
        let content_more_info = 'You can run the SPARQL query directly in the triplestore on the link: <a target="_blank" href="http://localhost:7200/sparql?name=&infer=true&sameAs=true&query='+query_link+'">query</a>';
        content_more_info+= '<span class="feedback_panel">';
        content_more_info+= ' <i title="this answer is correct!" onclick="feedback('+responseData['id']+',1)" class="fa-solid fa-thumbs-up feedback like"></i> <i title="this answer is incorrect!" onclick="feedback('+responseData['id']+',0)" class="fa-solid fa-thumbs-down feedback dislike"></i>';
        content_more_info+='</span>'
      this.pushMessage(1, content_more_info);
      }
      this.state.isTyping = false;
      this.setState(this.state);
    })
    .catch(error => {
      console.error('Error sending request:', error);
      this.state.isTyping = false;
      this.setState(this.state);
      this.pushMessage(1, "I'm sorry! something went wrong while trying to answer your question.");
    });
    input.value = "";
  }

  pushMessage(recipient = 0, message) {
    let sender = "Auto-KGQA";
    if(recipient == 0)
      sender = "User";
    const prevState = this.state;
    const newMessage = new Message({
      id: recipient,
      message,
      senderName: sender
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
let user_id = null;
if(cookies.get('user_id') == null){
  user_id = (Math.random()*1000)|0;
  cookies.set('user_id', user_id, { path: '/' });
  // console.log("criou novo user_id:"+user_id);
}else{
  user_id = cookies.get('user_id');
  // console.log("Carregou user_id:"+user_id);
}
const StyleChat = withStyles(muiStyles)(Chat);
render(<StyleChat user_id={user_id}/>, document.getElementById("root"));
