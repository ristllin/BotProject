import React, { Component } from 'react';
import './App.css';
import {Nombot} from './components/Nombot';

class App extends Component {
  constructor (props){
    super(props);
    this.menuButtonClickHander = this.menuButtonClickHander.bind(this);
    this.state = {
      pageName : "Nombot",
    }
  }

  menuButtonClickHander (buttonPressed){
    this.setState({
      pageName: buttonPressed,
    })
  }

  render() {
  //   // Build menu
  //   let menuItems = [
  //     {name: 'Nombot'},
  //  ]
  //  let menuDiv = 
  //  <div> 
  //   {menuItems.map((menuItem, i)=> (
  //       <ul className = 'Menu-Title' key={i}>
  //           <li><div onClick={(i)=> this.menuButtonClickHander(menuItem.name)}>{menuItem.name}</div></li>
  //       </ul>
  //     ))
  //   }
  // </div>

  // build component
  let pageComponent;
    switch (this.state.pageName) {
      case "Nombot":
        pageComponent = <Nombot></Nombot>;
        break;
      default:
        pageComponent = <Nombot></Nombot>;
        break;
    }
    return (
      <div className = "App">
        {/* <div className = "App-Menu">
          {menuDiv}
        </div> */}
        <div className = "content">
          {pageComponent}
        </div>
        <div className = "footer">
          <footer>
            <b>NomBot By Roy</b>

            
          </footer>
        </div>
      </div>
    );
  }
}

export default App;