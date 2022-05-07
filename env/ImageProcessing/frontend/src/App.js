import logo from './logo.svg';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import input from './elon.jpg';
import share0 from './sample_share0.png';
import share1 from './sample_share1.png';
import share2 from './sample_share2.png';
import down_arrow from './down_arrow.png';
import axios from 'axios';
import FormData from 'form-data';


class App extends Component {
  constructor(props) {
    super(props);
    this.state = { key:'',shares: '', minShares: '', inputImg: '', file: '', id: '' };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleImageChange = this.handleImageChange.bind(this);
  }


  handleChange(event) {
    this.setState({ [event.target.name]: event.target.value });
    console.log(this.state)

  }
  handleImageChange(event) {
    this.setState({ [event.target.name]: URL.createObjectURL(event.target.files[0]) });
    this.setState({ file: event.target.files[0] });
    console.log(this.state)

  }


  handleSubmit(event) {
    event.preventDefault();
    console.log(this.state)


    if (this.state.shares == 1) {
      alert("Shares cant be just 1")
    }

    else if (this.state.shares <= this.state.minShares) {
      alert("Shares must be greater than Minimum shares to recontruct")
    }
    else if (this.state.minShares < 2) {
      alert("Minimum Shares must be greater than 2")
    }

    else {

      const payload = {
        "n": Number(this.state.shares),
        "k": Number(this.state.minShares),
        "inputImage": this.state.inputImg,
        "outputImage": "",
        "cipher": "",
        "finalOutput": ""
      }
      // console.log(payload)
      var dataF = new FormData();
      dataF.append('inputImage', this.state.file);
      dataF.append('k', this.state.minShares);
      dataF.append('n', this.state.shares);

      var outputShares = []

      axios({
        method: "post",
        url: "http://127.0.0.1:8000/api/images/",
        data: dataF,
        headers: { "Content-Type": "multipart/form-data" },
      })

        .then(response => {
          this.setState({ status: response.status })
          this.setState({ id: [response.data.id] }, () => {
            console.log(this.state.id);
          })
          let id = response.data.id;
          console.log(JSON.stringify(response.data));

          if (this.state.id != null) {

            axios({
              method: "get",
              url: "http://127.0.0.1:8000/api/images/" + id + "/",
              headers: { "Content-Type": "multipart/form-data" },
            })
              .then(response => {
                console.log(JSON.stringify(response.data));
    
                axios({
                  method: "post",
                  url: "http://127.0.0.1:8000/post/" + id + "/",
                  headers: { "Content-Type": "multipart/form-data" },
                })
                  .then(response => {
                    console.log(JSON.stringify(response.data));
                    outputShares = response.data
                  })
                  .catch(error => {
                    console.log(error)
                  })
    
              })
              .catch(error => {
                console.log(error)
              })
          }
             this.setState({shares_img: outputShares})
        }
        )
        .catch(error => {
          console.log(error)
        })

      

    }

  }

  render() {

    const inputs = [];
    const images_shares =[];
      for (let i = 1; i <= this.state.shares; i++) {
      inputs.push(
         <input type="text" class="form-control" value={this.state.key[i]} onChange={this.handleChange} name={`key${i}`} placeholder="Enter Key For Encryption" required />
      )
    }
    return (



      <div className="App">
        <nav class="navbar sticky-top navbar-light bg-light">
          <div class="navbar-header">
            <a class="navbar-brand" href="#">PixSkew</a>
          </div>
          <div class="d-flex flex-row">
            <button class="btn btn-success navbar-btn me-1">Encrypt</button>
            <button class="btn btn-success navbar-btn">Decrypt</button>
          </div>
        </nav>
        <body>
          <div class="text-center">
            <h1>
              <span>Welcome</span>
              <span>To</span>
              <span>PixSkew!</span>
            </h1>
          </div>
          <div class="text-center">
            <h1 >
              <span>Send</span>
              <span>Secret</span>
              <span>Info</span>
              <span>Securely</span>
              <span>to</span>
              <span>your</span>
              <span>Friends!</span>
            </h1>
          </div>


          <div>
            <h1 style={{ align: "left" }}>Step 1</h1>
          </div>
          <div class="text-center">
            <img src={input} class="rounded" style={{ marginBottom: "20px", marginTop: "20px" }} alt="Input Image" />
          </div>
          <div class="text-center">
            <img src={down_arrow} class="rounded" style={{ marginBottom: "20px", marginTop: "20px", maxHeight: "100px" }} alt="flow" />
          </div>
          <div class="text-center">
            <img src={share0} class="rounded" style={{ marginRight: "10px" }} alt="Output Image" />
            <img src={share1} class="rounded" style={{ marginRight: "10px" }} alt="Output Image" />
            <img src={share2} class="rounded" style={{ marginRight: "10px" }} alt="Output Image" />
          </div>

          <div class="container center_div" style={{ maxWidth: "50vw" }}>
            <form class="formcss" onSubmit={this.handleSubmit} >
              <div class="form-group row">
                <label for="inputShares" class="col-sm-2 col-form-label" style={{ minWidth: "100px" }}>Number of Shares</label>
                <div class="col-sm-10">
                  <input type="text" class="form-control" value={this.state.shares} onChange={this.handleChange} name="shares" placeholder="Number of Shares you want to split the Image!" required />
                </div>
              </div>
              <div class="form-group row">
                <label for="inputMinShares" class="col-sm-2 col-form-label" style={{ minWidth: "100px" }}>Minimum Shares</label>
                <div class="col-sm-10">
                  <input type="text" class="form-control" value={this.state.minShares} onChange={this.handleChange} name="minShares" placeholder="Minimum Number of shares needed to recreate the Image!" required />
                </div>
              </div>

              <div class="form-group row">
                <label for="InputImage" class="col-sm-2 col-form-label" style={{ minWidth: "100px" }}>Insert Image</label>
                <div class="col-sm-4">

                  <div>
                    <img src={this.state.inputImg ? this.state.inputImg : null} alt={this.state.inputImg ? this.state.inputImg : null} class="img-thumbnail" />
                    <input type="file" name="inputImg" onChange={this.handleImageChange} required />
                  </div>
                </div>

              </div>
              <button type="submit" class="btn btn-primary" style={{ marginTop: "1vh" }}>Submit</button>
            </form>

            <form class="formcss" onSubmit={this.handleSubmit} >
             <div class="form-group row">
                <label for="key" class="col-sm-2 col-form-label" style={{ minWidth: "100px" }}>key for Encryption</label>
                <div class="col-sm-10">
                  {inputs}
                </div>
              </div>
              <button type="submit" class="btn btn-primary" style={{ marginTop: "1vh" }}>Submit</button>
            </form>

                <div>
                    {images_shares}
                </div>

          </div>
        </body>
      </div>
    );
  }
}
export default App;