import React from 'react';
import PropTypes from 'prop-types';
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
  children: PropTypes.object.isRequired, // eslint-disable-line react/forbid-prop-types
};

export default App;
