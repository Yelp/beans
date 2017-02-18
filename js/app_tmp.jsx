import React from 'react';
import Header from './components/Header';
import Footer from './components/Footer';

function App(props) {
  return (
    <div>
      <Header />
      {props.children}
      <Footer />
    </div>
  );
}

App.propTypes = {
  children: React.PropTypes.object.isRequired, // eslint-disable-line react/forbid-prop-types
};

export default App;
