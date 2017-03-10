/* eslint-env mocha */
import { expect } from '../../test_helper';
import { FETCH_METRICS, getMetrics } from '../../../js/actions/index';


describe('actions', () => {
  describe('getMetric', () => {
    it('has the correct type', () => {
      const metrics = getMetrics('v1');
      expect(metrics.type).to.equal(FETCH_METRICS);
    });
  });
  describe('getPreferences', () => {
    it('has the correct type', () => {
      const metrics = getMetrics('v1');
      expect(metrics.type).to.equal(FETCH_METRICS);
    });
  });
  describe('getUser', () => {
    it('has the correct type', () => {
      const metrics = getMetrics('v1');
      expect(metrics.type).to.equal(FETCH_METRICS);
    });
  });
});
