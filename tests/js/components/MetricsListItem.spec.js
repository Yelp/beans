/* eslint-env mocha */
import { expect } from 'chai';

import MetricsListItem from '../../../js/components/MetricsListItem';
import { renderComponent } from '../../test_helper';


describe('MetricsListItem', () => {
  let component;

  describe('without data', () => {
    beforeEach(() => {
      component = renderComponent(MetricsListItem);
    });

    it('prints malformatted if no data', () => {
      expect(component).to.contain('Malformatted');
    });
  });

  describe('with one subscription', () => {
    beforeEach(() => {
      const metrics = { metric: { title: 'weekly', subscribed: 10, meetings: 20 } };
      component = renderComponent(MetricsListItem, metrics);
    });

    it('has a title', () => {
      expect(component.find('.panel-heading')).to.contain('weekly');
    });

    it('has total subscribed', () => {
      expect(component.find('.list-group-item:nth-child(1)')).to.have.text('Total Subscribed: 10');
    });

    it('has total meetings', () => {
      expect(component.find('.list-group-item:nth-child(2)')).to.have.text('Total Meetings: 20');
    });
  });

  describe('with many subscriptions', () => {
    beforeEach(() => {
      const metrics = {
        // metric: { title: 'weekly', subscribed: 10, meetings: 20 },
        metric: { title: 'monthly', subscribed: 2, meetings: 4 },
      };
      component = renderComponent(MetricsListItem, metrics);
    });

    it('has multiple elements', () => {
      expect(component.find('.list-group-item').length).to.equal(2);
    });
  });
});
