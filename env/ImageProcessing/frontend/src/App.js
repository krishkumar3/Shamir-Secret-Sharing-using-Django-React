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
import loading from './loading.gif';
import LoadingOverlay from 'react-loading-overlay';
import axios from 'axios';
import Signin from './decrypt.jsx';
import HomePage from './encrypt.jsx';
import FormData from 'form-data';
import fileDownload from 'js-file-download';
const images = require.context('./outputs', true);
const initialstate = { file1:'', decryptoutput:false,page:"Encrypt",status1: "HomePage", loading: false, shares: '', minShares: '', inputImg: '', file: '', id: '', showKeyField: false, disabled: false, encrypt: true };
const Logout = { status1: "SignIn", loading: false, shares: '', minShares: '', inputImg: '', file: '', id: '', showKeyField: false, disabled: false, encrypt: true };


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {file1:'',Useremail:"", decryptoutput:false,page:"Encrypt",status1: "SignIn", loading: false, shares: '', minShares: '', inputImg: '', file: '', id: '', showKeyField: false, disabled: false, encrypt: true };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleImageChange = this.handleImageChange.bind(this);
    this.handleState = this.handleState.bind(this);
    this.handleSubmitForEncryption = this.handleSubmitForEncryption.bind(this);
    this.handlePageChange = this.handlePageChange.bind(this);
    this.handleSubmitDecryption = this.handleSubmitDecryption.bind(this);
    this.handleFileChange = this.handleFileChange.bind(this);
    this.handleFileChange1 = this.handleFileChange1.bind(this);
    this.handleKeys = this.handleKeys.bind(this);
    this.handleKeyState = this.handleKeyState.bind(this);
    this.setStateDefault = this.setStateDefault.bind(this);

  }

  setStateDefault() {
    this.setState(initialstate)
  }
  handleChange(event) {
    this.setState({ [event.target.name]: event.target.value });
    console.log(this.state);
  }
  handleImageChange(event) {
    this.setState({ [event.target.name]: URL.createObjectURL(event.target.files[0]) });
    this.setState({ file: event.target.files[0] });
    console.log(this.state)

  }
  handleState(value) {
    this.setState({ shares_img: value });
    this.setState({ showKeyField: true })
  }

  handleKeyState(key, value) {
    this.setState({ [key]: value });
    console.log(this.state)
  }

  handleSubmit(event) {
    event.preventDefault();
    console.log(this.state);

    this.setState({ disabled: true });
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
                    this.handleState(response.data)
                  })
                  .catch(error => {
                    console.log(error)
                  })

              })
              .catch(error => {
                console.log(error)
              })
          }

        }
        )
        .catch(error => {
          console.log(error)
        })



    }

  }

  handlePageChange(event) {
    console.log(event.target.value);
    if (event.target.value == "Encrypt") {
      this.setState({ page: "Encrypt" })

    }
    console.log("logout")
    if (event.target.value == "Decrypt") {
      this.setState({ page: "Decrypt" })
    }
    if(event.target.value == "Share"){
      this.setState({page:"Share"})
    }
    if(event.target.value == "Logout"){
      this.setState(Logout);
      console.log("logout")

    }
  }
  handleSubmitForEncryption(event) {
    event.preventDefault();
    console.log(this.state)
    const key = [];
    const id = this.state.id;
    for (let i = 0; i <= this.state.shares; i++) {
      key.push(this.state[`key${i + 1}`])
    }
    console.log(key);
    axios({
      method: "post",
      url: "http://127.0.0.1:8000/encrypt/" + this.state.id + "/",
      data: key,
      headers: { "Content-Type": "application/json" },
    })
      .then(response => {
        console.log(JSON.stringify(response.data));
        // window.open("http://127.0.0.1:8000/keyout/" + id + "/");
        // window.open("http://127.0.0.1:8000/cipher/" + id + "/");
        // window.location.reload(true);

        axios.get("http://127.0.0.1:8000/keyout/" + id + "/", {
          responseType: 'blob',
        })
          .then((res) => {
            fileDownload(res.data, "Keys.txt")
          })

        axios.get("http://127.0.0.1:8000/cipher/" + id + "/", {
          responseType: 'blob',
        })
          .then((res) => {
            fileDownload(res.data, "cipher_text.txt")
            this.setStateDefault()
          })

      })
      .catch(error => {
        console.log(error)
      })
  }
  handleSubmitDecryption(event) {
    event.preventDefault();
    console.log(this.state);
    this.setState({ loading: true })

    this.setState({ disabled: true });

    var dataF = new FormData();
    dataF.append('cipher', this.state.file);
    dataF.append('keys', this.state.file1);
    let k = this.state.minShares;
    axios({ 
      method: "post",
      url: "http://127.0.0.1:8000/api/cipher/",
      data: dataF,
      headers: { "Content-Type": "multipart/form-data" },
    })

      .then(response => {
        console.log(JSON.stringify(response.data));
        let id = response.data.id;
        axios({
          method: "post",
          url: "http://127.0.0.1:8000/decrypt/" + id + "/",
          headers: { "Content-Type": "application/json" },
        })
          .then(response => {
            console.log(JSON.stringify(response.data));
            this.handleKeyState("status", response.data);
            this.handleKeyState("loading", false);
            this.handleKeyState("decryptoutput", true);
            console.log(this.state);
          })
          .catch(error => {
            console.log(error)
          })

      }
      )
      .catch(error => {
        console.log(error)
      })




  }

  handleKeys(event) {
    const num = this.state.shares;
    const keys = [];

    axios({
      method: "post",
      url: "http://127.0.0.1:8000/keygen/" + num + "/",
      headers: { "Content-Type": "application/json" },
    })
      .then(response => {
        let keys = response.data
        console.log("keys", keys);
        for (let i = 0; i <= num; i++) {
          let key_id = `key${i + 1}`;
          this.handleKeyState(key_id, keys[i]);
        }
      })
      .catch(error => {
        console.log(error)
      });


  }
  handleFileChange(event) {
    this.setState({ [event.target.name]: URL.createObjectURL(event.target.files[0]) });
    this.setState({ file: event.target.files[0] });
    console.log(this.state)
  }
  handleFileChange1(event) {
    this.setState({ [event.target.name]: URL.createObjectURL(event.target.files[0]) });
    this.setState({ file1: event.target.files[0] });
    console.log(this.state)
  }
  render() {

    const inputs = [];
    const output = [];
    const images_shares = [];
    let i = 1
    for (; i <= this.state.shares; i++) {
      inputs.push(
        <div class="form-group row" style={{ padding: "10px" }}>
          <label for={`key${i}`} class="col-sm-2 col-form-label">{`Share ${i}`}</label>
          <div class="col-sm-10">
            <input type="text" class="form-control" minlength="10" value={this.state[`key${i}`]} onChange={this.handleChange} name={`key${i}`} placeholder={`Enter Key For Encrypting share ${i}`} required />
          </div>
        </div>
      )
    }

    if (this.state.shares.length > 0) {
      inputs.push(
        <div class="form-group row" style={{ padding: "10px" }}>
          <label for={`key${i}`} class="col-sm-2 col-form-label">Total Cipher</label>
          <div class="col-sm-10">
            <input type="text" class="form-control" minlength="10" value={this.state[`key${i}`]} onChange={this.handleChange} name={`key${i}`} placeholder="Enter Key For Encrypting the Cipher Text Output" required />
          </div>
        </div>
      )

      if (this.state.encrypt == true) {
        inputs.push(


          <div class="form-group row" style={{ padding: "10px" }}>
            <div class="col-sm-10">
              <button type="button" class="btn btn-primary" onClick={this.handleKeys} style={{ marginTop: "1vh" }}> Auto Fill Keys</button>
            </div>
          </div>
        )
      }
    }
    if (this.state.shares_img != null) {
      console.log(this.state);
      for (let j = 0; j < this.state.shares; j++) {
        const dynamicImage = `outputs/${this.state.shares_img.images[j]}`;
        console.log(dynamicImage);
        images_shares.push(
          <div class="col-sm">
            <img src={dynamicImage} class="img-thumbnail" alt={"share" + j} />
          </div>
        )
      }
    }

    if (this.state.decryptoutput == true) {
      console.log(this.state);

      const dynamicImage = `outputs/originalimage.png`;
      console.log(dynamicImage);
      output.push(
        <div class="col-sm">
          <img src={dynamicImage} class="img-thumbnail" alt="original image" />
        </div>
      )

    }
    return (

      <div className='Main'>

        {this.state.status1 == "SignIn" && <Signin Signin={this.handleKeyState} />}
        {this.state.status1 == "HomePage" && <div className="App">
          <nav class="navbar sticky-top navbar-light bg-light">
            <div class="navbar-header">
              <a class="navbar-brand" href="#">PixSkew</a>
            </div>
            <div class="d-flex flex-row">
              <button class="btn btn-success navbar-btn me-1" value="Share" onClick={this.handlePageChange}>Share</button>
              <button class="btn btn-success navbar-btn me-1" value="Encrypt" onClick={this.handlePageChange}>Encrypt</button>
              <button class="btn btn-success navbar-btn me-1" value="Decrypt" onClick={this.handlePageChange}>Decrypt</button>
              <button class="btn btn-success navbar-btn" value="Logout" onClick={this.handlePageChange}>Logout</button>
            </div>
          </nav>

          {this.state.page == "Share" && <HomePage {...this.state} handleKeyState = {this.handleKeyState}/> }

          {this.state.page == "Encrypt" && <body>

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
                    <input type="number" min="2" max="6" class="form-control" value={this.state.shares} onChange={this.handleChange} name="shares" placeholder="Number of Shares you want to split the Image!" required />
                  </div>
                </div>
                <div class="form-group row">
                  <label for="inputMinShares" class="col-sm-2 col-form-label" style={{ minWidth: "100px" }}>Minimum Shares</label>
                  <div class="col-sm-10">
                    <input type="number" min="2" max="6" class="form-control" value={this.state.minShares} onChange={this.handleChange} name="minShares" placeholder="Minimum Number of shares needed to recreate the Image!" required />
                  </div>
                </div>

                <div class="form-group row">
                  <label for="InputImage" class="col-sm-2 col-form-label" style={{ minWidth: "100px" }}>Insert Image</label>
                  <div class="col-sm-4">

                    <div>
                      <img src={this.state.inputImg ? this.state.inputImg : null} alt={this.state.inputImg ? this.state.inputImg : null} class="img-thumbnail" />
                      <input type="file" name="inputImg" accept=".jpg" onChange={this.handleImageChange} required />
                    </div>
                  </div>

                </div>
                <button type="submit" class="btn btn-primary" disabled={this.state.disabled} style={{ marginTop: "1vh" }}>Submit</button>
                {!this.state.showKeyField && this.state.disabled && <img class="loading" src={loading} alt="Loading..." />}
              </form>



              {this.state.showKeyField &&

                <div>

                  <div>
                    <h1 style={{ align: "left" }}>Step 2</h1>
                  </div>

                  <div class="container">
                    <div class="row">
                      {images_shares}
                    </div>
                  </div>

                  <div class="text-center">
                    <img src={down_arrow} class="rounded" style={{ marginBottom: "20px", marginTop: "20px", maxHeight: "100px" }} alt="flow" />
                  </div>

                  <div class="text-center">
                    <h1 style={{ align: "center" }}>AES Encryption</h1>
                  </div>


                  <form class="formcss" onSubmit={this.handleSubmitForEncryption} >
                    <div class="form-group row">
                      <h2>Enter key for Encrypting each Share</h2>
                      {inputs}
                    </div>
                    <button type="submit" class="btn btn-primary" style={{ marginTop: "1vh" }}>Submit</button>
                  </form>
                </div>
              }

            </div>
          </body>}


          {
            this.state.page == "Decrypt" &&
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



              <div class="text-center">
                <h2>Enter the Cipher Text file</h2>
              </div>

              <div class="container center_div" style={{ maxWidth: "50vw" }}>



                <form class="formcss" onSubmit={this.handleSubmitDecryption} >
                  {/* <div class="form-group row">
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
                </div> */}

                  <div class="form-group row">
                    <label for="InputCipher" class="col-sm-2 col-form-label" style={{ minWidth: "100px" }}>Insert Cipher File</label>
                    <div class="col-sm-4">

                      <div>
                        <input type="file" name="inputCipher" accept="text/plain" onChange={this.handleFileChange} required />
                      </div>
                    </div>

                  </div>

                  <div class="form-group row">
                    <label for="InputKey" class="col-sm-2 col-form-label" style={{ minWidth: "100px" }}>Insert Key File</label>
                    <div class="col-sm-4">

                      <div>
                        <input type="file" name="inputKey"  accept="text/plain" onChange={this.handleFileChange1} required />
                      </div>
                    </div>

                  </div>

                  <div>

                    <div class="form-group row">
                      {this.state.shares.length > 0 && <h3>Enter key for Decrypting Shares</h3>}
                      {inputs}
                    </div>
                  </div>

                  <button type="submit" class="btn btn-primary" disabled={this.state.disabled} style={{ marginTop: "1vh" }}>Submit</button>
                  {this.state.loading && <img class="loading" src={loading} alt="Loading..." />}




                </form>

                {this.state.decryptoutput == true
                  && <div class="form-group row">
                    {output}
                  </div>
                }


              </div>
            </body>
          }
        </div>
        }
      </div>


    );

  }

}
export default App;
