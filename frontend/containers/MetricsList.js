import axios from 'axios';
import React, { Component } from 'react';

import MetricsListItem from '../components/MetricsListItem';

class MetricsList extends Component {
  constructor(props) {
    super(props);
    this.state = { metrics: [{ subscribed: 0, title: 'No Subscriptions', meetings: 0 }] };
  }

  componentDidMount() {
    axios.get('/v1/metrics/').then(
      (res) => { this.setState({ metrics: res.data }); },
    );
  }

  renderMetrics() {
    const { metrics } = this.state;
    return metrics.map((metric) => (
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

export default MetricsList;
