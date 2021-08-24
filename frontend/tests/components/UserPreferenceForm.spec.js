import React from 'react';
import renderer from 'react-test-renderer';

import UserPreferenceForm from '../../components/UserPreferenceForm';


describe('UserPreferenceForm', () => {
  it('is rendered with one subscription', () => {
    const preferences = [
      {
        "datetime":[
          {
            "active":true,
            "auto_renew":false,
            "date":"2021-03-25T22:00:00+00:00",
            "id":27
          }
        ],
        "id":20,
        "location":"Online",
        "office":"Remote",
        "rule_logic":"any",
        "size":2,
        "timezone":"America/Los_Angeles",
        "title":"iOS Weekly (all offices welcome, please set up your own time/place)"
      }
    ];
    const component = renderer.create(<UserPreferenceForm preferences={preferences} email="test@gmail.com" />);
    const json = component.toJSON()
    expect(json).toMatchSnapshot();
    expect(true);
  });
});
