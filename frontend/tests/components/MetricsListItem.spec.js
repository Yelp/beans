import React from 'react';
import renderer from 'react-test-renderer';

import MetricsListItem from '../../components/MetricsListItem';


describe('MetricsListItem', () => {
  it('is rendered with one subscription', () => {
    const metric = { title: 'weekly', total_subscribed: 10, week_participants: 20 };
    const component = renderer.create(<MetricsListItem metric={metric} />);
    expect(component.toJSON()).toMatchSnapshot();
  });

  it('is rendered with many subscriptions', () => {
    const metric = { title: 'monthly', total_subscribed: 2, week_participants: 4 };
    const component = renderer.create(<MetricsListItem metric={metric} />);
    expect(component.toJSON()).toMatchSnapshot();
  });
});
