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
import LoadingOverlay from 'react-loading-overlay';
import axios from 'axios';
import loading from './loading.gif';
import fileDownload from 'js-file-download';
import FormData from 'form-data';
const images = require.context('./outputs', true);
const Logout = { status1: "SignIn", loading: false, shares: '', minShares: '', inputImg: '', file: '', id: '', showKeyField: false, disabled: false, encrypt: true };
const email = (props) => (
  this.handleKeyState("Useremail", props.email)
);
class HomePage extends Component {
  constructor(props) {
    super(props);
    this.state = { showLoading:false ,receiverEmail: '', shares: '', minShares: '', inputImg: '', file: '', id: '', showKeyField: false, disabled: false };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleImageChange = this.handleImageChange.bind(this);
    this.handleState = this.handleState.bind(this);
    this.handleKeys = this.handleKeys.bind(this);
    this.handleKeyState = this.handleKeyState.bind(this);
    this.handleSubmitForEncryption = this.handleSubmitForEncryption.bind(this);
    this.handleSubmitForDecryption = this.handleSubmitForDecryption.bind(this);
    this.handleFileChange = this.handleFileChange.bind(this);


  }

  componentDidMount() {
    this.handleKeyState("Useremail", this.props.Useremail)
    console.log(this.state);
    console.log(this.props);
    axios({
      method: "post",
      url: "http://127.0.0.1:8000/sharedimages/" + this.props.Useremail + "/",
      headers: { "Content-Type": "multipart/form-data" },
    })
      .then(response => {
        console.log(JSON.stringify(response.data));
        this.setState({ images_shared: response.data })
        // this.handleState(response.data)
      })
      .catch(error => {
        console.log(error)
      })


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
    console.log(this.state)
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

      var emailshareData = new FormData();
      emailshareData.append('useremail', this.state.receiverEmail);
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
          emailshareData.append('coreId', id)
          emailshareData.append('fromemail', this.state.Useremail)
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


                axios({
                  method: "post",
                  url: "http://127.0.0.1:8000/api/emailshare/",
                  headers: { "Content-Type": "multipart/form-data" },
                  data: emailshareData
                })
                  .then(response => {
                    console.log(JSON.stringify(response.data));
                    // this.handleState(response.data)
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
    if (event.target.value == "Share") {
      this.setState({ page: "Share" })
    }
    if (event.target.value == "Logout") {
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
            fileDownload(res.data, "KeysFor" + id + ".txt")
          })

        // axios.get("http://127.0.0.1:8000/cipher/" + id + "/", {
        //   responseType: 'blob',
        // })
        //   .then((res) => {
        //     fileDownload(res.data, "cipher_text.txt")
        //     this.setStateDefault()
        //   })

      })
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

  handleSubmitForDecryption(event,pk) {
    event.preventDefault();
    // let pk = event.target.value;
    console.log("working" + pk)
    var dataF = new FormData();
    dataF.append('keys', this.state.file);

    this.handleKeyState("showLoading",true);
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
          url: "http://127.0.0.1:8000/decryptshared/" + id + "/" +pk + "/",
          headers: { "Content-Type": "application/json" },
        })
          .then(response => {
            console.log(JSON.stringify(response.data));
            // this.handleKeyState("status", response.data);
            // this.handleKeyState("loading", false);
            // this.handleKeyState("decryptoutput", true);
            console.log(this.state);
            if(response.data == 200){
                    axios.get("http://127.0.0.1:8000/outputs/originalimage.png/", {
                      responseType: 'blob',
                    })
                      .then((res) => {
                        fileDownload(res.data, "outputImage.png")
                      })
                      this.handleKeyState("showLoading",false);
                    }
            else{
              alert("Error in decryption");
              this.props.handleKeyState("page", "Encrypt");

            }
            
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

  handleFileChange(event) {
    this.setState({ [event.target.name]: URL.createObjectURL(event.target.files[0]) });
    this.setState({ file: event.target.files[0] });
    console.log(this.state)
  }

  render() {

    const inputs = [];
    const images_shares = [];
    const shared = [];
    let i = 1
    for (; i <= this.state.shares; i++) {
      inputs.push(
        <div class="form-group row" style={{ padding: "10px" }}>
          <label for={`key${i}`} class="col-sm-2 col-form-label">{`Share ${i}`}</label>
          <div class="col-sm-10">
            <input type="text" class="form-control" value={this.state[`key${i}`]} onChange={this.handleChange} name={`key${i}`} placeholder={`Enter Key For Encrypting share ${i}`} required />
          </div>
        </div>
      )
    }

    inputs.push(
      <div class="form-group row" style={{ padding: "10px" }}>
        <label for={`key${i}`} class="col-sm-2 col-form-label">Total Cipher</label>
        <div class="col-sm-10">
          <input type="text" class="form-control" value={this.state[`key${i}`]} onChange={this.handleChange} name={`key${i}`} placeholder="Enter Key For Encrypting the Cipher Text Output" required />
        </div>
      </div>
    )

    inputs.push(


      <div class="form-group row" style={{ padding: "10px" }}>
        <div class="col-sm-10">
          <button type="button" class="btn btn-primary" onClick={this.handleKeys} style={{ marginTop: "1vh" }}> Auto Fill Keys</button>
        </div>
      </div>
    )
    if (this.state.images_shared != null) {
      for (let iter = 0; iter < Number(this.state.images_shared.count); iter++) {
        shared.push(
          <form class="formcss" onSubmit={(event) => this.handleSubmitForDecryption(event,this.state.images_shared.data[iter]["pk"])}>
            <div class="form-group row">
              <h5> {iter + 1}. Image #{this.state.images_shared.data[iter]["pk"]} from: {this.state.images_shared.data[iter]["from"]}  </h5>
              <br></br>
              <label for="keyFile" class="col-sm-2 col-form-label" style={{ minWidth: "100px", marginTop: "10px" }}>Key File</label>
              <div class="col-sm-10" style={{marginTop:"10px"}}>
                <input type="file" name="inputKeys"  accept="text/plain" onChange={this.handleFileChange} required />
              </div>
              <br></br>
              <br></br>

            </div>
            <button type="submit" className="btn btn-primary" value={this.state.images_shared.data[iter]["pk"]}> Decrypt </button>
          </form>
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

    return (
      <div className="App">
        <body>


          <div class="container center_div" style={{ maxWidth: "50vw" }}>
            <div>
              <br></br>
              <h3>Share Images With Friends</h3>
            </div>

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
                    <input type="file" name="inputImg" onChange={this.handleImageChange} required />
                  </div>
                </div>

              </div>

              <div class="form-group row">
                <label for="ReceiverEmail" class="col-sm-2 col-form-label" style={{ minWidth: "100px" }}>Receiver Email</label>
                <div class="col-sm-10">
                  <input type="email" class="form-control" value={this.state.receiverEmail} onChange={this.handleChange} name="receiverEmail" placeholder="Enter Receiver Email" required />
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
        </body>
        <div>
          <br></br>

          <div class="container" style={{ maxWidth: "50vw" }}>
              <h3>Images Shared With Me</h3>
              {shared}
              {this.state.showLoading && <img class="loading" src={loading} alt="Loading..." />}
          </div>
        </div>

      </div>
    );
  }
}
export default HomePage;
