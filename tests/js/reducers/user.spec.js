/* eslint-env mocha */
import { expect } from 'chai';
import UserReducer from '../../../js/reducers/user';
import { FETCH_USER } from '../../../js/actions';


describe('UserReducer', () => {
  it('handles action of getUser', () => {
    const action = {
      type: FETCH_USER,
      payload: { data: [{ email: 'darwin@yelp.com' }] },
    };
    expect(UserReducer([], action)[0].email).to.equal('darwin@yelp.com');
  });
});
