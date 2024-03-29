import React from "react";

function Footer() {
  return (
    <div>
      <hr className="footer_hr" />
      <div className="container">
        <div className="row">
          <div className="w-100 text-center">
            <h5>
              <small>Made with ♥ at Yelp.</small>
            </h5>
            <a href="https://github.com/Yelp/beans">
              <img
                className="github-img"
                alt="Github Logo"
                src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
              />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Footer;
