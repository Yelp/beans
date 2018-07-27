import React from 'react';
import PropTypes from 'prop-types';


const MetricsListItem = ({ metric }) => (
  <div className="panel panel-danger">
    <div className="panel-heading">
      {metric.title}
    </div>
    <ul className="list-group">
      <li className="list-group-item">
          Total Subscribed:
        {metric.total_subscribed}
      </li>
      <li className="list-group-item">
          Participants this week:
        {metric.week_participants}
      </li>
    </ul>
  </div>
);

MetricsListItem.propTypes = {
  metric: PropTypes.object.isRequired, // eslint-disable-line react/forbid-prop-types
};

export default MetricsListItem;
