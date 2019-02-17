import React, { Component } from 'react';
import "./Nombot.css";
import '../Fonts.css';

class Nombot extends Component {
    constructor (props){
      super(props);
      console.log("Nombot component constructed");
      //States
      this.state = {
          userString: "User response",
          resultData : undefined
      }
      //Fields
      this.result = "Hello";

      //Bindings
      this.PostString = this.PostString.bind(this);
      this.inputOnChange = this.inputOnChange.bind(this);
    }

    PostString(event){
        if (this.state.WTString !== undefined && this.state.VarString !== undefined) { //check strings exist
            var url = '/sequence_submition';
            var data = {"User": this.state.userString};
            console.log("Post Strings:",data);
            fetch(url, {
                method: 'POST',
                body: JSON.stringify(data),
                headers: {'Accept': 'application/json','Content-Type': 'application/json'},
                })
                .then(response => response.json())
                .then(data => this.setState({resultData:JSON.parse(data)}))
                .catch(error => console.error('Error:', error));
                console.log("data recieved: ",this.state.resultData);
        }
        else {
            alert("Please fill input before submition");
        }
    }

    inputOnChange(event){
        this.setState({WTString: event.target.value});
    }

    shouldComponentUpdate(nextProps, nextState){
        console.log("debug",nextState.resultData);
        if (this.state.resultData !== undefined && nextState.userEvents !== undefined){ 
            if(!(this.state.resultData).equals(nextState.userEvents)){
                return true
            }
        }
        return true
    }


    render() {
        console.log("Nombot component rendered");
        let result = undefined;
        if (this.state.resultData !== undefined ){
            result = 
            <div>
                <br></br>
                <br></br>
                <b>Result:</b>
                <br></br>
                <p>{this.state.resultData['ANSWER']}</p>
            </div>
        }


        return (
            <div> 
                <h1 className='Header'> {/*header */}
                    Nombot
                </h1> 
                <form>
                    <b>Talk to Nombot here:</b><br></br>
                    <input type="text" name="UserInput" onChange={this.inputOnChange} value={this.state.inputString}/><br></br>
                    <br></br>
                </form>
                <button className = "Analyze-button" onClick = {this.PostString}>Send</button>
                <br></br>
                {result}
            </div>
        );
    }
}
export {Nombot};