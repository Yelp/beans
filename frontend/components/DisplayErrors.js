import React from "react";
import PropTypes from "prop-types";

const ErrorMessageShape = PropTypes.shape({
  loc: PropTypes.arrayOf(
    PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  ),
  msg: PropTypes.string.isRequired,
});

function DisplayErrorMessage({ errors }) {
  return (
    <div className="alert alert-danger mb-2" role="alert">
      Error saving subscription.
      <ul>
        {errors.map((error) => (
          <li key={JSON.stringify(error)}>
            {error.loc && `${error.loc.join(".")}: `}
            {error.msg}
          </li>
        ))}
      </ul>
    </div>
  );
}

DisplayErrorMessage.propTypes = {
  errors: PropTypes.arrayOf(ErrorMessageShape).isRequired,
};

export default DisplayErrorMessage;
