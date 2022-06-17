
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import React, { Component } from 'react';
import { HashRouter as Router, Route, Link, NavLink } from 'react-router-dom';
import ReactDOM from 'react-dom';
import axios from 'axios';
import { SocialIcon } from 'react-social-icons';
import FormData from 'form-data';
import share0 from './sample_share01.png';

class Signin extends Component {
  constructor(props) {
    super(props);
    this.state = {};

    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.handleRegister = this.handleRegister.bind(this);
    this.handleForgotPassword = this.handleForgotPassword.bind(this);
    this.makeid = this.makeid.bind(this);
  }

  handleChange(e) {
    this.state.error = '';
    let target = e.target;
    let value = target.value;
    let name = target.name;

    this.setState({
      [name]: value
    });
    console.log(this.state);
    // console.log("Id:"+this.makeid())
  }

  makeid() {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    var numbers = '0123456789';
    var charactersLength = characters.length;
    var numberLength = numbers.length;
    for (var i = 0; i < 5; i++) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    for (var i = 0; i < 5; i++) {
      result += numbers.charAt(Math.floor(Math.random() * numberLength));
    }
    return result;
  }

  handleRegister(e) {
    e.preventDefault();

    this.setState({ loggedIn: true })

    var dataF = new FormData();
    var username = this.makeid();
    dataF.append('email', this.state.email);
    dataF.append('password', this.state.password);
    dataF.append('username', this.makeid());

    axios({
      method: "post",
      url: "http://127.0.0.1:8000/api/users/",
      data: dataF,
      headers: { "Content-Type": "multipart/form-data" },
    })
      .then(response => {
        this.setState({ status: response.status })

        if (response.status == 200) {
          this.setState({ loggedIn: true })
        }
        alert("User created Successfully!")
      })
      .catch(error => {
        console.log(error)
        this.setState({
          status: 400
        })
        alert("Unable to create User, Email Already exists")
      })


  }


  handleForgotPassword(e) {
    e.preventDefault();

    if (this.state.email != null) {
      axios({
        method: "post",
        url: "http://127.0.0.1:8000/sendEmail/" + this.state.email + "/",
        headers: { "Content-Type": "multipart/form-data" },
      })
        .then(response => {
          if (response.status == 200) {
            this.setState({ loggedIn: true })
          }
          alert("Mail Sent Successfully!")
        })
        .catch(error => {
          console.log(error)
          this.setState({
            status: 400
          })
          alert("Unable to send Email")
        })
    }
    else {
      alert("Enter Email")
    }

  }



  handleSubmit(e) {
    e.preventDefault();

    axios({
      method: "post",
      url: "http://127.0.0.1:8000/signin/" + this.state.email + "/" + this.state.password + "/",
      headers: { "Content-Type": "multipart/form-data" },
    })
      .then(response => {
        var status = response.data.status;
        var reason = response.data.reason;
        this.setState({ status: status })

        if (status == 200) {
          this.setState({ loggedIn: true });
          this.props.Signin("status1", "HomePage")
          this.props.Signin("Useremail", this.state.email)
        }

        if (status == 400) {
          alert(reason)
        }
      })
      .catch(error => {
        console.log(error)
        alert(error)
      })


  }
  render() {



    return (
      <div className="App">

        <body style={{ backgroundImage: `url(${share0})` }}>

          <div className="FormCenter">
            <form onSubmit={this.handleSubmit} className="FormFields">
              <div className="FormField">
                <h3>PikSkew</h3>
                <br></br>
              </div>
              <div className="FormField">
                <label className="FormField__Label" htmlFor="email">E-Mail Address</label>
                <input type="email" id="email" className="FormField__Input" placeholder="Enter your email" name="email" value={this.state.email} onChange={this.handleChange} />
              </div>

              <div className="FormField">
                <label className="FormField__Label" htmlFor="password">Password</label>
                <input type="password" id="password" className="FormField__Input" placeholder="Enter your password" name="password" value={this.state.password} onChange={this.handleChange} />
              </div>
              <div className="gap">
                <div className="FormField">
                  <button className="FormField__Button mr-20">Sign In</button>
                  {/* <NavLink to="/forgot" className="FormField__Link">Forgot Password? </NavLink> */}
                </div>
                <div className="FormField">
                  <button type="button" onClick={this.handleRegister} className="FormField__Button mr-20">Register</button>
                  {/* <NavLink to="/forgot" className="FormField__Link">Forgot Password? </NavLink> */}
                </div>
                <div className="FormField">
                  <button type="button" onClick={this.handleForgotPassword} title="Enter Email in the above" id="forgotpassword" className="FormField__Button mr-20">Forgot Password?</button>
                  {/* <NavLink to="/forgot" className="FormField__Link">Forgot Password? </NavLink> */}
                </div>
              </div>





              <div className="space">
                <center>
                  <div />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                </center>
              </div>


            </form>
          </div>

        </body>

      </div>
    );
  }
}
export default Signin;
