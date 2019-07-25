import PrefReducer from '../../reducers/preferences';
import { FETCH_PREFS } from '../../actions';


describe('PrefReducer', () => {
  it('handles action of getPrefs', () => {
    const action = {
      type: FETCH_PREFS,
      payload: { data: [{ title: 'metrics' }] },
    };
    expect(PrefReducer([], action)[0].title).toBe('metrics');
  });
});
