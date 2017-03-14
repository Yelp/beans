import React from 'react';


const MetricsListItem = ({ metric }) => {
  if (!metric) {
    return <div>Malformatted</div>;
  }
  return (
    <div className="panel panel-danger">
      <div className="panel-heading">{metric.title}</div>
      <ul className="list-group">
        <li className="list-group-item">
          Total Subscribed: {metric.subscribed}
        </li>
        <li className="list-group-item">
          Total Meetings: {metric.meetings}
        </li>
      </ul>
    </div>
  );
};

MetricsListItem.propTypes = {
  metric: React.PropTypes.object.isRequired, // eslint-disable-line react/forbid-prop-types
};

export default MetricsListItem;
