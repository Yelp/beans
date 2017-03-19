import React from 'react';
import renderer from 'react-test-renderer';
import MetricsListItem from '../../../js/components/MetricsListItem';


describe('MetricsListItem', () => {
  it('is rendered without data', () => {
    const component = renderer.create(<MetricsListItem />);
    expect(component.toJSON()).toMatchSnapshot();
  });

  it('is rendered with one subscription', () => {
    const metric = { title: 'weekly', subscribed: 10, meetings: 20 };
    const component = renderer.create(<MetricsListItem metric={metric} />);
    expect(component.toJSON()).toMatchSnapshot();
  });

  it('is rendered with many subscriptions', () => {
    const metric = { title: 'monthly', subscribed: 2, meetings: 4 };
    const component = renderer.create(<MetricsListItem metric={metric} />);
    expect(component.toJSON()).toMatchSnapshot();
  });
});
