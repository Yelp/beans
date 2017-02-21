import { expect } from '../../test_helper';
import MetricsReducer from '../../../js/reducers/metrics'
import { getMetrics, FETCH_METRICS } from '../../../js/actions'


describe('MetricsReducer', () => {
    it('handles action of getMetrics', () => {
        var action = {
            type: FETCH_METRICS,
            payload: {data: [{title:'metrics'}]}
        };
        expect(MetricsReducer([], action)[0]['title']).to.equal('metrics');
    });
});
