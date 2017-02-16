import React, { Component } from 'react';
import { connect } from 'react-redux';
import { getMetrics } from '../actions/index';

import MetricsListItem from '../components/MetricsListItem';


class MetricsList extends Component {
  componentWillMount() {
    this.props.getMetrics('v1');
  }
  renderMetrics() {
    return this.props.metrics.map(metric => (
      <MetricsListItem
        key={metric.title}
        metric={metric}
      />
            ));
  }
  render() {
    return (
      <div className="container-fluid">
        {this.renderMetrics()}
      </div>
    );
  }
}

MetricsList.propTypes = {
  getMetrics: React.PropTypes.func.isRequired,
  metrics: React.PropTypes.array.isRequired, // eslint-disable-line react/forbid-prop-types
};

function mapStateToProps(state) {
  return { metrics: state.metrics };
}

export default connect(mapStateToProps, { getMetrics })(MetricsList);
