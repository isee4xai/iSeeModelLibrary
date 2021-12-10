"use strict";

module.exports.retrieval = async (event) => {
  return {
    statusCode: 200,
    body: JSON.stringify(
      {
        message: "Welcome to the first iSee retrieval service.",
        query: event.body,
      },
      null,
      2
    ),
  };
};
